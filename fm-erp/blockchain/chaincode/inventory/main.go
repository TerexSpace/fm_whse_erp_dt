package main

import (
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

func main() {
	inventoryChaincode, err := contractapi.NewChaincode(&InventoryContract{})
	if err != nil {
		fmt.Printf("Error creating inventory chaincode: %v\n", err)
		return
	}

	if err := inventoryChaincode.Start(); err != nil {
		fmt.Printf("Error starting inventory chaincode: %v\n", err)
	}
}
