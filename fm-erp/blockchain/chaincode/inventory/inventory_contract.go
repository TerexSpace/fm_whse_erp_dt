package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// InventoryContract manages warehouse inventory on blockchain
type InventoryContract struct {
	contractapi.Contract
}

// Product represents an inventory item
type Product struct {
	ID              string    `json:"id"`
	SKU             string    `json:"sku"`
	Name            string    `json:"name"`
	Quantity        int       `json:"quantity"`
	WarehouseID     string    `json:"warehouseId"`
	Location        string    `json:"location"`
	LastUpdated     time.Time `json:"lastUpdated"`
	QualityScore    float64   `json:"qualityScore"`
	Temperature     float64   `json:"temperature"`
	Humidity        float64   `json:"humidity"`
}

// Transaction represents an inventory transaction
type Transaction struct {
	ID              string    `json:"id"`
	Type            string    `json:"type"` // IN, OUT, TRANSFER, ADJUST
	ProductID       string    `json:"productId"`
	Quantity        int       `json:"quantity"`
	SourceWarehouse string    `json:"sourceWarehouse"`
	DestWarehouse   string    `json:"destWarehouse"`
	Timestamp       time.Time `json:"timestamp"`
	InitiatedBy     string    `json:"initiatedBy"`
	DataQuality     float64   `json:"dataQuality"`
}

// InitLedger initializes the chaincode with sample data
func (c *InventoryContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	products := []Product{
		{
			ID:           "PROD001",
			SKU:          "SKU-A001",
			Name:         "Widget A",
			Quantity:     100,
			WarehouseID:  "WH001",
			Location:     "A-01-01",
			LastUpdated:  time.Now(),
			QualityScore: 0.98,
			Temperature:  22.5,
			Humidity:     45.0,
		},
		{
			ID:           "PROD002",
			SKU:          "SKU-B002",
			Name:         "Widget B",
			Quantity:     250,
			WarehouseID:  "WH002",
			Location:     "B-02-03",
			LastUpdated:  time.Now(),
			QualityScore: 0.95,
			Temperature:  23.1,
			Humidity:     48.5,
		},
	}

	for _, product := range products {
		productJSON, err := json.Marshal(product)
		if err != nil {
			return err
		}

		err = ctx.GetStub().PutState(product.ID, productJSON)
		if err != nil {
			return fmt.Errorf("failed to put product to world state: %v", err)
		}
	}

	return nil
}

// CreateProduct adds a new product to the ledger
func (c *InventoryContract) CreateProduct(ctx contractapi.TransactionContextInterface, 
	id, sku, name string, quantity int, warehouseID, location string) error {
	
	exists, err := c.ProductExists(ctx, id)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("product %s already exists", id)
	}

	product := Product{
		ID:           id,
		SKU:          sku,
		Name:         name,
		Quantity:     quantity,
		WarehouseID:  warehouseID,
		Location:     location,
		LastUpdated:  time.Now(),
		QualityScore: 1.0,
	}

	productJSON, err := json.Marshal(product)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, productJSON)
}

// ReadProduct retrieves a product from the ledger
func (c *InventoryContract) ReadProduct(ctx contractapi.TransactionContextInterface, id string) (*Product, error) {
	productJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if productJSON == nil {
		return nil, fmt.Errorf("product %s does not exist", id)
	}

	var product Product
	err = json.Unmarshal(productJSON, &product)
	if err != nil {
		return nil, err
	}

	return &product, nil
}

// UpdateQuantity modifies product quantity and records transaction
func (c *InventoryContract) UpdateQuantity(ctx contractapi.TransactionContextInterface,
	productID string, quantityChange int, txType, initiatedBy string) error {
	
	product, err := c.ReadProduct(ctx, productID)
	if err != nil {
		return err
	}

	// Update quantity
	newQuantity := product.Quantity + quantityChange
	if newQuantity < 0 {
		return fmt.Errorf("insufficient inventory: current=%d, requested=%d", product.Quantity, quantityChange)
	}

	product.Quantity = newQuantity
	product.LastUpdated = time.Now()

	// Calculate data quality score (PoDQ consensus metric)
	dataQuality := c.calculateDataQuality(product)

	// Record transaction
	transaction := Transaction{
		ID:              fmt.Sprintf("TX-%d", time.Now().Unix()),
		Type:            txType,
		ProductID:       productID,
		Quantity:        quantityChange,
		SourceWarehouse: product.WarehouseID,
		Timestamp:       time.Now(),
		InitiatedBy:     initiatedBy,
		DataQuality:     dataQuality,
	}

	transactionJSON, err := json.Marshal(transaction)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(transaction.ID, transactionJSON)
	if err != nil {
		return fmt.Errorf("failed to record transaction: %v", err)
	}

	// Update product state
	productJSON, err := json.Marshal(product)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(productID, productJSON)
}

// calculateDataQuality implements PoDQ consensus metric
func (c *InventoryContract) calculateDataQuality(product *Product) float64 {
	// PoDQ formula: DQ = (completeness + accuracy + timeliness) / 3
	
	// Completeness: check all required fields are populated
	completeness := 1.0
	if product.Temperature == 0 || product.Humidity == 0 {
		completeness = 0.8
	}

	// Accuracy: based on quality score
	accuracy := product.QualityScore

	// Timeliness: decay based on last update (1.0 if < 1 hour old)
	timeSinceUpdate := time.Since(product.LastUpdated).Hours()
	timeliness := 1.0
	if timeSinceUpdate > 1 {
		timeliness = 1.0 / (1.0 + timeSinceUpdate/24.0) // Decay over days
	}

	return (completeness + accuracy + timeliness) / 3.0
}

// GetAllProducts returns all products in the ledger
func (c *InventoryContract) GetAllProducts(ctx contractapi.TransactionContextInterface) ([]*Product, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var products []*Product
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var product Product
		err = json.Unmarshal(queryResponse.Value, &product)
		if err != nil {
			continue // Skip invalid entries
		}

		products = append(products, &product)
	}

	return products, nil
}

// ProductExists checks if product exists in ledger
func (c *InventoryContract) ProductExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	productJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return productJSON != nil, nil
}

// TransferProduct transfers inventory between warehouses
func (c *InventoryContract) TransferProduct(ctx contractapi.TransactionContextInterface,
	productID string, quantity int, destWarehouse, initiatedBy string) error {
	
	product, err := c.ReadProduct(ctx, productID)
	if err != nil {
		return err
	}

	if product.Quantity < quantity {
		return fmt.Errorf("insufficient quantity for transfer")
	}

	// Reduce quantity at source
	err = c.UpdateQuantity(ctx, productID, -quantity, "TRANSFER_OUT", initiatedBy)
	if err != nil {
		return err
	}

	// Record transfer transaction
	transaction := Transaction{
		ID:              fmt.Sprintf("TX-TRANSFER-%d", time.Now().Unix()),
		Type:            "TRANSFER",
		ProductID:       productID,
		Quantity:        quantity,
		SourceWarehouse: product.WarehouseID,
		DestWarehouse:   destWarehouse,
		Timestamp:       time.Now(),
		InitiatedBy:     initiatedBy,
		DataQuality:     c.calculateDataQuality(product),
	}

	transactionJSON, err := json.Marshal(transaction)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(transaction.ID, transactionJSON)
}
