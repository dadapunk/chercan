"""Database exporter for Crawl4AI.

This module provides functionality for exporting crawled content
into various database systems.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Iterable, Type
import json
import os
import logging
from datetime import datetime
import importlib
from abc import ABC, abstractmethod

from crawl4ai.exports.base_exporter import BaseExporter
from crawl4ai.models import Page, CrawlResult


logger = logging.getLogger(__name__)


class DBConnector(ABC):
    """Abstract base class for database connectors.
    
    This class defines the interface that all database connectors must implement.
    Each connector is responsible for managing the connection to a specific
    database system and providing methods to save data.
    """
    
    @abstractmethod
    def connect(self, **connection_params):
        """Establish a connection to the database.
        
        Args:
            **connection_params: Connection parameters specific to the database
            
        Returns:
            Connection object or None if connection failed
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the database connection."""
        pass
    
    @abstractmethod
    def save_item(self, collection: str, item: Dict[str, Any]) -> bool:
        """Save a single item to the database.
        
        Args:
            collection: Collection/table name
            item: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def save_items(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Save multiple items to the database.
        
        Args:
            collection: Collection/table name
            items: List of data items to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def save_page(self, collection: str, page: Page) -> bool:
        """Save a Page object to the database.
        
        Args:
            collection: Collection/table name
            page: Page object to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def save_pages(self, collection: str, pages: List[Page]) -> bool:
        """Save multiple Page objects to the database.
        
        Args:
            collection: Collection/table name
            pages: List of Page objects to save
            
        Returns:
            True if successful, False otherwise
        """
        pass


class SQLiteConnector(DBConnector):
    """Connector for SQLite database.
    
    This connector allows storing crawled data in an SQLite database,
    which is a lightweight, disk-based database.
    """
    
    def __init__(self, db_path: str = "crawl4ai_data.db"):
        """Initialize the SQLite connector.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self, **connection_params):
        """Connect to the SQLite database.
        
        Args:
            **connection_params: Additional connection parameters
            
        Returns:
            Connection object if successful, None otherwise
        """
        try:
            import sqlite3
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return self.conn
        except ImportError:
            logger.error("sqlite3 is not available. Please install it.")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {str(e)}")
            return None
    
    def disconnect(self):
        """Close the SQLite database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def _ensure_table(self, collection: str):
        """Ensure the collection table exists.
        
        Args:
            collection: Table name to create if not exists
        """
        if not self.conn:
            self.connect()
        
        # Create table if it doesn't exist
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {collection} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data JSON,
            url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()
    
    def save_item(self, collection: str, item: Dict[str, Any]) -> bool:
        """Save a single item to the SQLite database.
        
        Args:
            collection: Table name
            item: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        try:
            self._ensure_table(collection)
            
            # Convert item to JSON string
            data_json = json.dumps(item)
            url = item.get('url', '')
            
            # Insert the data
            self.cursor.execute(f"INSERT INTO {collection} (data, url) VALUES (?, ?)",
                               (data_json, url))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save item to SQLite: {str(e)}")
            return False
    
    def save_items(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Save multiple items to the SQLite database.
        
        Args:
            collection: Table name
            items: List of data items to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        try:
            self._ensure_table(collection)
            
            # Prepare data for batch insertion
            batch_data = []
            for item in items:
                data_json = json.dumps(item)
                url = item.get('url', '')
                batch_data.append((data_json, url))
            
            # Insert the data batch
            self.cursor.executemany(f"INSERT INTO {collection} (data, url) VALUES (?, ?)",
                                   batch_data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save items to SQLite: {str(e)}")
            return False
    
    def save_page(self, collection: str, page: Page) -> bool:
        """Save a Page object to the SQLite database.
        
        Args:
            collection: Table name
            page: Page object to save
            
        Returns:
            True if successful, False otherwise
        """
        # Create a dictionary representation of the page
        data = {
            'url': getattr(page, 'url', ''),
            'title': getattr(page, 'title', ''),
            'status_code': getattr(page, 'status_code', 0),
            'content_type': getattr(page, 'content_type', ''),
            'depth': getattr(page, 'depth', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add page data if available
        if hasattr(page, 'data') and isinstance(page.data, dict):
            data['data'] = page.data
        
        return self.save_item(collection, data)
    
    def save_pages(self, collection: str, pages: List[Page]) -> bool:
        """Save multiple Page objects to the SQLite database.
        
        Args:
            collection: Table name
            pages: List of Page objects to save
            
        Returns:
            True if successful, False otherwise
        """
        items = []
        for page in pages:
            # Create a dictionary representation of the page
            data = {
                'url': getattr(page, 'url', ''),
                'title': getattr(page, 'title', ''),
                'status_code': getattr(page, 'status_code', 0),
                'content_type': getattr(page, 'content_type', ''),
                'depth': getattr(page, 'depth', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add page data if available
            if hasattr(page, 'data') and isinstance(page.data, dict):
                data['data'] = page.data
            
            items.append(data)
        
        return self.save_items(collection, items)


class MongoDBConnector(DBConnector):
    """Connector for MongoDB database.
    
    This connector allows storing crawled data in a MongoDB database,
    which is a document-oriented database.
    """
    
    def __init__(self, database: str = "crawl4ai", **kwargs):
        """Initialize the MongoDB connector.
        
        Args:
            database: Name of the MongoDB database
            **kwargs: Additional parameters for the MongoDB client
        """
        self.database_name = database
        self.client = None
        self.db = None
        self.client_kwargs = kwargs
    
    def connect(self, **connection_params):
        """Connect to the MongoDB database.
        
        Args:
            **connection_params: Connection parameters (host, port, etc.)
            
        Returns:
            Database object if successful, None otherwise
        """
        try:
            # Import pymongo here to avoid dependency if not used
            import pymongo
            
            # Merge connection_params with client_kwargs
            params = {**self.client_kwargs, **connection_params}
            
            # Set default host and port if not provided
            if 'host' not in params:
                params['host'] = 'localhost'
            if 'port' not in params:
                params['port'] = 27017
            
            # Create MongoDB client
            self.client = pymongo.MongoClient(**params)
            
            # Connect to the database
            self.db = self.client[self.database_name]
            
            # Ping the database to verify connection
            self.client.admin.command('ping')
            
            return self.db
        except ImportError:
            logger.error("pymongo is not available. Please install it with 'pip install pymongo'.")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return None
    
    def disconnect(self):
        """Close the MongoDB database connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
    
    def save_item(self, collection: str, item: Dict[str, Any]) -> bool:
        """Save a single item to the MongoDB database.
        
        Args:
            collection: Collection name
            item: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            self.connect()
        
        try:
            # Get the collection
            coll = self.db[collection]
            
            # Add timestamp if not present
            if 'timestamp' not in item:
                item['timestamp'] = datetime.now()
            
            # Insert the document
            result = coll.insert_one(item)
            
            return result.acknowledged
        except Exception as e:
            logger.error(f"Failed to save item to MongoDB: {str(e)}")
            return False
    
    def save_items(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Save multiple items to the MongoDB database.
        
        Args:
            collection: Collection name
            items: List of data items to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            self.connect()
        
        try:
            # Get the collection
            coll = self.db[collection]
            
            # Add timestamp to each document if not present
            for item in items:
                if 'timestamp' not in item:
                    item['timestamp'] = datetime.now()
            
            # Insert multiple documents
            result = coll.insert_many(items)
            
            return result.acknowledged
        except Exception as e:
            logger.error(f"Failed to save items to MongoDB: {str(e)}")
            return False
    
    def save_page(self, collection: str, page: Page) -> bool:
        """Save a Page object to the MongoDB database.
        
        Args:
            collection: Collection name
            page: Page object to save
            
        Returns:
            True if successful, False otherwise
        """
        # Create a dictionary representation of the page
        data = {
            'url': getattr(page, 'url', ''),
            'title': getattr(page, 'title', ''),
            'status_code': getattr(page, 'status_code', 0),
            'content_type': getattr(page, 'content_type', ''),
            'depth': getattr(page, 'depth', 0),
            'timestamp': datetime.now()
        }
        
        # Add page data if available
        if hasattr(page, 'data') and isinstance(page.data, dict):
            data['data'] = page.data
        
        return self.save_item(collection, data)
    
    def save_pages(self, collection: str, pages: List[Page]) -> bool:
        """Save multiple Page objects to the MongoDB database.
        
        Args:
            collection: Collection name
            pages: List of Page objects to save
            
        Returns:
            True if successful, False otherwise
        """
        items = []
        for page in pages:
            # Create a dictionary representation of the page
            data = {
                'url': getattr(page, 'url', ''),
                'title': getattr(page, 'title', ''),
                'status_code': getattr(page, 'status_code', 0),
                'content_type': getattr(page, 'content_type', ''),
                'depth': getattr(page, 'depth', 0),
                'timestamp': datetime.now()
            }
            
            # Add page data if available
            if hasattr(page, 'data') and isinstance(page.data, dict):
                data['data'] = page.data
            
            items.append(data)
        
        return self.save_items(collection, items)


class DatabaseExporter(BaseExporter):
    """Exporter for database storage.
    
    This class provides functionality to export crawled content to various
    database systems using database-specific connectors.
    
    Example:
    ```python
    # Create a database exporter with SQLite connector
    exporter = DatabaseExporter(connector=SQLiteConnector(db_path="crawl_data.db"))
    
    # Export content to the database
    exporter.export_content(content, collection="products")
    
    # Export a page to the database
    exporter.export_page(page, collection="pages")
    ```
    """
    
    def __init__(
        self,
        connector: DBConnector = None,
        connector_type: str = "sqlite",
        collection: str = "crawl_data",
        auto_connect: bool = True,
        **connector_params
    ):
        """Initialize the database exporter.
        
        Args:
            connector: Database connector instance
            connector_type: Type of connector to create if not provided
            collection: Default collection/table name
            auto_connect: Whether to connect automatically
            **connector_params: Parameters to pass to the connector
        """
        super().__init__()
        self.collection = collection
        
        # Use provided connector or create one based on type
        if connector:
            self.connector = connector
        else:
            self.connector = self._create_connector(connector_type, **connector_params)
        
        # Connect if auto_connect is True
        if auto_connect and self.connector:
            self.connector.connect(**connector_params)
    
    def _create_connector(self, connector_type: str, **connector_params) -> Optional[DBConnector]:
        """Create a database connector of the specified type.
        
        Args:
            connector_type: Type of connector to create
            **connector_params: Parameters to pass to the connector
            
        Returns:
            Database connector instance or None if type is invalid
        """
        connector_map = {
            "sqlite": SQLiteConnector,
            "mongodb": MongoDBConnector,
        }
        
        if connector_type.lower() in connector_map:
            return connector_map[connector_type.lower()](**connector_params)
        else:
            logger.error(f"Unsupported connector type: {connector_type}")
            return None
    
    def export_content(self, content: Dict[str, Any], collection: str = None) -> str:
        """Export content to the database.
        
        Args:
            content: Dictionary containing the content to export
            collection: Optional collection/table name override
            
        Returns:
            JSON string representation of the content for compatibility
        """
        # Use specified collection or default
        coll = collection or self.collection
        
        # Save to database
        if self.connector:
            self.connector.save_item(coll, content)
        
        # Return JSON representation for compatibility with other exporters
        return json.dumps(content)
    
    def export_page(self, page: Page, collection: str = None) -> str:
        """Export a Page object to the database.
        
        Args:
            page: Page object to export
            collection: Optional collection/table name override
            
        Returns:
            JSON string representation of the page for compatibility
        """
        # Use specified collection or default
        coll = collection or self.collection
        
        # Save to database
        if self.connector:
            self.connector.save_page(coll, page)
        
        # Create a JSON representation for compatibility
        page_dict = {
            "url": getattr(page, "url", ""),
            "title": getattr(page, "title", ""),
            "status_code": getattr(page, "status_code", 0),
            "content_type": getattr(page, "content_type", ""),
        }
        
        if hasattr(page, "data") and page.data:
            page_dict["data"] = page.data
        
        return json.dumps(page_dict)
    
    def export_multiple(self, contents: Iterable[Dict[str, Any]], collection: str = None) -> str:
        """Export multiple content dictionaries to the database.
        
        Args:
            contents: Iterable of content dictionaries to export
            collection: Optional collection/table name override
            
        Returns:
            JSON string representation of the contents for compatibility
        """
        # Convert to list
        contents_list = list(contents)
        
        # Use specified collection or default
        coll = collection or self.collection
        
        # Save to database
        if self.connector and contents_list:
            self.connector.save_items(coll, contents_list)
        
        # Return JSON representation for compatibility
        return json.dumps(contents_list)
    
    def export_pages(self, pages: Iterable[Page], collection: str = None) -> str:
        """Export multiple Page objects to the database.
        
        Args:
            pages: Iterable of Page objects to export
            collection: Optional collection/table name override
            
        Returns:
            JSON string representation of the pages for compatibility
        """
        # Convert to list
        pages_list = list(pages)
        
        # Use specified collection or default
        coll = collection or self.collection
        
        # Save to database
        if self.connector and pages_list:
            self.connector.save_pages(coll, pages_list)
        
        # Create a JSON representation for compatibility
        page_dicts = []
        for page in pages_list:
            page_dict = {
                "url": getattr(page, "url", ""),
                "title": getattr(page, "title", ""),
                "status_code": getattr(page, "status_code", 0),
                "content_type": getattr(page, "content_type", ""),
            }
            
            if hasattr(page, "data") and page.data:
                page_dict["data"] = page.data
            
            page_dicts.append(page_dict)
        
        return json.dumps(page_dicts)
    
    def export_crawl_result(self, result: CrawlResult, collection: str = None) -> str:
        """Export a CrawlResult object to the database.
        
        Args:
            result: CrawlResult object to export
            collection: Optional collection/table name override
            
        Returns:
            JSON string representation of the result for compatibility
        """
        if hasattr(result, 'pages') and result.pages:
            return self.export_pages(result.pages, collection)
        return ""
    
    def _join_multiple_exports(self, exports: List[str]) -> str:
        """Join multiple export results into a single string.
        
        Args:
            exports: List of exported content strings
            
        Returns:
            Combined string for multiple exports
        """
        # For database exporter, this is just for compatibility
        combined_data = []
        for export in exports:
            try:
                data = json.loads(export)
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)
            except json.JSONDecodeError:
                # Skip invalid JSON
                pass
        
        return json.dumps(combined_data)
    
    def close(self):
        """Close the database connection."""
        if self.connector:
            self.connector.disconnect()
    
    def __del__(self):
        """Ensure the database connection is closed when the exporter is deleted."""
        self.close() 