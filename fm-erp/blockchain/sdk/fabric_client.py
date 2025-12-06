"""
Hyperledger Fabric Python SDK Client for FM-ERP
Provides interface to interact with blockchain network
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

try:
    from hfc.fabric import Client
    from hfc.fabric.user import User
    from hfc.fabric.channel import Channel
except ImportError:
    # Mock classes for environment without fabric-sdk-py
    class Client:
        def __init__(self, net_profile=None): pass
        def new_channel(self, name): return Channel(name)
        def get_user(self, org, name): return User(name, org)
    class User:
        def __init__(self, name, org): pass
    class Channel:
        def __init__(self, name): pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BlockchainConfig:
    """Configuration for blockchain connection"""
    network_config_path: str = "blockchain/network/connection-profile.json"
    channel_name: str = "inventorychannel"
    chaincode_name: str = "inventory"
    org_name: str = "Warehouse1MSP"
    peer_name: str = "peer0.warehouse1.fmerp.com"
    orderer_name: str = "orderer.fmerp.com"
    user_name: str = "Admin"
    user_cert_path: str = "blockchain/network/crypto-config/peerOrganizations/warehouse1.fmerp.com/users/Admin@warehouse1.fmerp.com/msp/signcerts/Admin@warehouse1.fmerp.com-cert.pem"
    user_key_path: str = "blockchain/network/crypto-config/peerOrganizations/warehouse1.fmerp.com/users/Admin@warehouse1.fmerp.com/msp/keystore/priv_sk"


class FabricClient:
    """High-level client for interacting with Hyperledger Fabric network"""
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.client: Optional[Client] = None
        self.channel: Optional[Channel] = None
        self.user: Optional[User] = None
        
    async def connect(self) -> bool:
        """Establish connection to Fabric network"""
        try:
            # Initialize Fabric client
            self.client = Client(net_profile=self.config.network_config_path)
            
            # Get organization
            org = self.client.get_organization(self.config.org_name)
            
            # Load user credentials
            with open(self.config.user_cert_path, 'r') as cert_file:
                cert = cert_file.read()
            
            with open(self.config.user_key_path, 'r') as key_file:
                private_key = key_file.read()
            
            # Create user context
            self.user = self.client.get_user(
                org_name=self.config.org_name,
                name=self.config.user_name
            )
            
            if not self.user:
                self.user = User(
                    name=self.config.user_name,
                    org=self.config.org_name,
                    state_store=None
                )
                self.user.enrollment_secret = None
                
            # Get channel
            self.channel = self.client.new_channel(self.config.channel_name)
            
            logger.info(f"Successfully connected to Fabric network - Channel: {self.config.channel_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Fabric network: {e}")
            return False
    
    async def invoke_chaincode(
        self,
        function_name: str,
        args: List[str],
        transient_map: Optional[Dict] = None
    ) -> Dict:
        """
        Invoke chaincode function (writes to ledger)
        
        Args:
            function_name: Name of chaincode function to invoke
            args: List of string arguments
            transient_map: Optional transient data (not written to ledger)
            
        Returns:
            Transaction response
        """
        try:
            if not self.channel or not self.user:
                raise RuntimeError("Not connected to network. Call connect() first.")
            
            # Build transaction proposal
            tx_context = self.client.tx_context(
                user_context=self.user,
                prop_type='ENDORSER_TRANSACTION'
            )
            
            # Invoke chaincode
            response = await self.channel.chaincode_invoke(
                requestor=self.user,
                channel_name=self.config.channel_name,
                peers=[self.config.peer_name],
                args=args,
                cc_name=self.config.chaincode_name,
                fcn=function_name,
                transient_map=transient_map,
                wait_for_event=True,
                timeout=30
            )
            
            logger.info(f"Chaincode invoked: {function_name} - TxID: {response.get('tx_id')}")
            return {
                'success': True,
                'tx_id': response.get('tx_id'),
                'data': response
            }
            
        except Exception as e:
            logger.error(f"Chaincode invocation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def query_chaincode(
        self,
        function_name: str,
        args: List[str]
    ) -> Dict:
        """
        Query chaincode function (read-only, no write to ledger)
        
        Args:
            function_name: Name of chaincode function to query
            args: List of string arguments
            
        Returns:
            Query response
        """
        try:
            if not self.channel or not self.user:
                raise RuntimeError("Not connected to network. Call connect() first.")
            
            # Query chaincode
            response = await self.channel.chaincode_query(
                requestor=self.user,
                channel_name=self.config.channel_name,
                peers=[self.config.peer_name],
                args=args,
                cc_name=self.config.chaincode_name,
                fcn=function_name
            )
            
            # Parse response
            if response:
                data = json.loads(response)
                logger.info(f"Chaincode queried: {function_name}")
                return {
                    'success': True,
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'error': 'Empty response from chaincode'
                }
                
        except Exception as e:
            logger.error(f"Chaincode query failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_product(
        self,
        product_id: str,
        sku: str,
        name: str,
        quantity: int,
        warehouse_id: str,
        location: str
    ) -> Dict:
        """Create new product on blockchain"""
        args = [product_id, sku, name, str(quantity), warehouse_id, location]
        return await self.invoke_chaincode('CreateProduct', args)
    
    async def read_product(self, product_id: str) -> Dict:
        """Read product from blockchain"""
        return await self.query_chaincode('ReadProduct', [product_id])
    
    async def update_quantity(
        self,
        product_id: str,
        quantity_change: int,
        tx_type: str,
        initiated_by: str
    ) -> Dict:
        """Update product quantity and record transaction"""
        args = [product_id, str(quantity_change), tx_type, initiated_by]
        return await self.invoke_chaincode('UpdateQuantity', args)
    
    async def transfer_product(
        self,
        product_id: str,
        quantity: int,
        dest_warehouse: str,
        initiated_by: str
    ) -> Dict:
        """Transfer product between warehouses"""
        args = [product_id, str(quantity), dest_warehouse, initiated_by]
        return await self.invoke_chaincode('TransferProduct', args)
    
    async def get_all_products(self) -> Dict:
        """Retrieve all products from blockchain"""
        return await self.query_chaincode('GetAllProducts', [])


class BlockchainAdapter:
    """Adapter for blockchain interactions in FL client"""
    
    def __init__(self, network=None, config: Optional[BlockchainConfig] = None):
        self.network = network
        self.config = config or BlockchainConfig()
        self.client = FabricClient(self.config)
        
    def submit_hash(self, client_id: str, gradient_hash: str) -> str:
        """Submit gradient hash to blockchain"""
        # In a real implementation, this would invoke chaincode
        # For now/test, we can just log or return a dummy tx_id
        # or use self.client.invoke_chaincode if connected
        return f"tx_{hashlib.sha256((client_id + gradient_hash).encode()).hexdigest()[:16]}"


# Example usage
if __name__ == "__main__":
    async def main():
        config = BlockchainConfig()
        client = FabricClient(config)
        
        # Connect to network
        connected = await client.connect()
        if not connected:
            print("Failed to connect to blockchain network")
            return
        
        # Create product
        result = await client.create_product(
            product_id="PROD003",
            sku="SKU-C003",
            name="Widget C",
            quantity=500,
            warehouse_id="WH001",
            location="C-03-05"
        )
        print(f"Create Product Result: {result}")
        
        # Query product
        product = await client.read_product("PROD003")
        print(f"Product Details: {product}")
        
        # Get all products
        all_products = await client.get_all_products()
        print(f"All Products: {all_products}")
    
    asyncio.run(main())
