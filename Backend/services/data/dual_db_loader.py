"""
Dual Database Loader for SynGen AI
Loads CSV data into PostgreSQL and PDF documents into MongoDB
"""
import asyncio
import logging
import pandas as pd
import PyPDF2
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime
import json

# Local imports
from services.database.database_manager import DualDatabaseManager, get_database_manager
from models.database.postgresql import (
    Base, engine, SessionLocal,
    PaymentType, DeliveryStatus, ShippingMode, OrderStatus,
    Market, CustomerSegment, Category, Department, Country, State, 
    Customer, Product, Order, OrderItem
)
from models.database.mongodb import (
    PolicyDocument, DocumentStatus, MongoDBCollections,
    MongoDBIndexes, DocumentChunk
)

logger = logging.getLogger(__name__)

class DualDatabaseLoader:
    """Loads data into both PostgreSQL and MongoDB"""
    
    def __init__(self):
        self.db_manager = None
        
    async def initialize(self):
        """Initialize database manager"""
        self.db_manager = await get_database_manager()
        return self.db_manager is not None
    
    async def load_all_data(self):
        """Load all data into both databases"""
        if not await self.initialize():
            logger.error("Failed to initialize database manager")
            return False
        
        try:
            logger.info("🚀 Starting dual database data loading...")
            
            # Step 1: Create PostgreSQL schema
            logger.info("📋 Creating PostgreSQL schema...")
            await self._create_postgresql_schema()
            
            # Step 2: Create MongoDB indexes
            logger.info("🗂️ Creating MongoDB indexes...")
            await self._create_mongodb_indexes()
            
            # Step 3: Load CSV data into PostgreSQL
            logger.info("📊 Loading CSV data into PostgreSQL...")
            postgres_success = await self._load_csv_to_postgres()
            
            # Step 4: Load PDF documents into MongoDB
            logger.info("📚 Loading PDF documents into MongoDB...")
            mongodb_success = await self._load_pdfs_to_mongodb()
            
            if postgres_success and mongodb_success:
                logger.info("✅ All data loaded successfully!")
                await self._print_summary()
                return True
            else:
                logger.error("❌ Some data loading failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Data loading failed: {e}")
            return False
    
    async def _create_postgresql_schema(self):
        """Create PostgreSQL tables"""
        try:
            # Create tables using SQLAlchemy
            Base.metadata.create_all(bind=engine)
            logger.info("✅ PostgreSQL schema created")
        except Exception as e:
            logger.error(f"❌ PostgreSQL schema creation failed: {e}")
            raise
    
    async def _create_mongodb_indexes(self):
        """Create MongoDB indexes"""
        try:
            indexes = MongoDBIndexes.get_indexes()
            
            for collection_name, collection_indexes in indexes.items():
                for index_def in collection_indexes:
                    try:
                        db = await self.db_manager.mongodb.get_database()
                        
                        # Extract index options
                        index_key = index_def['key']
                        index_name = index_def['name']
                        
                        # Handle special index options
                        index_options = {"name": index_name}
                        if index_def.get('unique'):
                            index_options['unique'] = True
                        
                        # Create the index
                        await db[collection_name].create_index(
                            list(index_key.items()),
                            **index_options
                        )
                        
                        logger.debug(f"Created index {index_name} on {collection_name}")
                        
                    except Exception as e:
                        # Index might already exist, that's okay
                        logger.debug(f"Index creation warning for {collection_name}.{index_name}: {e}")
            
            logger.info("✅ MongoDB indexes created")
            
        except Exception as e:
            logger.error(f"❌ MongoDB index creation failed: {e}")
            raise
    
    async def _load_csv_to_postgres(self) -> bool:
        """Load CSV data into PostgreSQL"""
        try:
            csv_path = "../Supply_chain_database(dataco-supply-chain-dataset)/DataCoSupplyChainDataset.csv"
            
            if not Path(csv_path).exists():
                logger.error(f"CSV file not found: {csv_path}")
                return False
            
            # Load CSV with proper encoding
            df = pd.read_csv(csv_path, encoding='latin-1')
            logger.info(f"📁 Loaded CSV with {len(df)} rows")
            
            # Get PostgreSQL session
            session = self.db_manager.postgres.get_session()
            
            try:
                # Clear existing data
                logger.info("🧹 Clearing existing PostgreSQL data...")
                await self._clear_postgres_data(session)
                
                # Load reference data
                logger.info("📚 Loading reference data...")
                await self._load_reference_data(df, session)
                
                # Load main entities
                logger.info("👥 Loading customers...")
                await self._load_customers(df, session)
                
                logger.info("📦 Loading products...")
                await self._load_products(df, session)
                
                logger.info("📋 Loading orders...")
                await self._load_orders(df, session)
                
                logger.info("🛍️ Loading order items...")
                await self._load_order_items(df, session)
                
                session.commit()
                logger.info("✅ PostgreSQL data loaded successfully")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ PostgreSQL data loading failed: {e}")
                return False
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ CSV loading failed: {e}")
            return False
    
    async def _clear_postgres_data(self, session):
        """Clear existing PostgreSQL data"""
        # Use raw SQL for faster deletion
        tables_to_clear = [
            'order_items', 'orders', 'customers', 'products',
            'payment_types', 'delivery_statuses', 'shipping_modes', 
            'order_statuses', 'markets', 'customer_segments', 
            'categories', 'departments', 'countries', 'states'
        ]
        
        for table in tables_to_clear:
            try:
                session.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
            except:
                # Table might not exist yet
                pass
        session.commit()
    
    async def _load_reference_data(self, df, session):
        """Load reference data tables"""
        # Payment Types
        payment_types = df['Type'].dropna().unique()
        for pt in payment_types:
            if pt and pt != 'XXXXXXXXX':
                session.add(PaymentType(name=str(pt)))
        
        # Delivery Statuses
        delivery_statuses = df['Delivery Status'].dropna().unique()
        for ds in delivery_statuses:
            if ds and ds != 'XXXXXXXXX':
                session.add(DeliveryStatus(name=str(ds)))
        
        # Shipping Modes
        shipping_modes = df['Shipping Mode'].dropna().unique()
        for sm in shipping_modes:
            if sm and sm != 'XXXXXXXXX':
                session.add(ShippingMode(name=str(sm)))
        
        # Order Statuses
        order_statuses = df['Order Status'].dropna().unique()
        for os in order_statuses:
            if os and os != 'XXXXXXXXX':
                session.add(OrderStatus(name=str(os)))
        
        # Markets
        markets = df['Market'].dropna().unique()
        for market in markets:
            if market and market != 'XXXXXXXXX':
                session.add(Market(name=str(market)))
        
        # Customer Segments
        segments = df['Customer Segment'].dropna().unique()
        for segment in segments:
            if segment and segment != 'XXXXXXXXX':
                session.add(CustomerSegment(name=str(segment)))
        
        # Categories
        categories = df['Category Name'].dropna().unique()
        for category in categories:
            if category and category != 'XXXXXXXXX':
                session.add(Category(name=str(category)))
        
        # Departments
        departments = df['Department Name'].dropna().unique()
        for dept in departments:
            if dept and dept != 'XXXXXXXXX':
                session.add(Department(name=str(dept)))
        
        # Countries and States
        countries_states = df[['Customer Country', 'Customer State']].dropna().drop_duplicates()
        country_map = {}
        
        for _, row in countries_states.iterrows():
            country_name = str(row['Customer Country'])
            state_name = str(row['Customer State'])
            
            if country_name != 'XXXXXXXXX':
                # Add country if not exists
                if country_name not in country_map:
                    country = Country(name=country_name)
                    session.add(country)
                    session.flush()  # Get the ID
                    country_map[country_name] = country.id
                
                # Add state
                if state_name != 'XXXXXXXXX':
                    state = State(name=state_name, country_id=country_map[country_name])
                    session.add(state)
        
        session.commit()
        logger.info("✅ Reference data loaded")
    
    async def _load_customers(self, df, session):
        """Load customer data"""
        # Get reference data mappings
        segments_map = {s.name: s.id for s in session.query(CustomerSegment).all()}
        countries_map = {c.name: c.id for c in session.query(Country).all()}
        states_map = {s.name: s.id for s in session.query(State).all()}
        
        # Get unique customers
        customers_df = df[[
            'Customer Id', 'Customer Fname', 'Customer Lname', 'Customer Email',
            'Customer Password', 'Customer Street', 'Customer City', 'Customer State',
            'Customer Country', 'Customer Zipcode', 'Customer Segment'
        ]].drop_duplicates(subset=['Customer Id'])
        
        customers_added = 0
        
        for _, row in customers_df.iterrows():
            try:
                # Skip invalid records
                customer_id = row['Customer Id']
                if pd.isna(customer_id) or customer_id in ['XXXXXXXXX', '']:
                    continue
                
                # Get segment ID
                segment_name = str(row['Customer Segment']).strip()
                segment_id = segments_map.get(segment_name)
                
                # Get state ID
                state_name = str(row['Customer State']).strip()
                state_id = states_map.get(state_name)
                
                customer = Customer(
                    customer_id=int(customer_id),
                    first_name=str(row['Customer Fname']).strip(),
                    last_name=str(row['Customer Lname']).strip(),
                    email=str(row['Customer Email']).strip(),
                    password_hash=str(row['Customer Password']).strip(),
                    street=str(row['Customer Street']).strip(),
                    city=str(row['Customer City']).strip(),
                    zipcode=str(row['Customer Zipcode']).strip(),
                    segment_id=segment_id,
                    state_id=state_id
                )
                
                session.add(customer)
                customers_added += 1
                
                # Commit in batches
                if customers_added % 1000 == 0:
                    session.commit()
                    logger.info(f"Loaded {customers_added} customers...")
                    
            except Exception as e:
                logger.warning(f"Failed to load customer {row.get('Customer Id', 'unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"✅ Loaded {customers_added} customers")
    
    async def _load_products(self, df, session):
        """Load product data"""
        # Get reference data mappings
        categories_map = {c.name: c.id for c in session.query(Category).all()}
        departments_map = {d.name: d.id for d in session.query(Department).all()}
        
        # Get unique products
        products_df = df[[
            'Product Card Id', 'Product Name', 'Product Category Id', 'Category Name',
            'Department Id', 'Department Name', 'Product Price', 'Product Status'
        ]].drop_duplicates(subset=['Product Card Id'])
        
        products_added = 0
        
        for _, row in products_df.iterrows():
            try:
                # Skip invalid records
                product_id = row['Product Card Id']
                if pd.isna(product_id) or product_id in ['XXXXXXXXX', '']:
                    continue
                
                # Get category and department IDs
                category_name = str(row['Category Name']).strip()
                category_id = categories_map.get(category_name)
                
                department_name = str(row['Department Name']).strip()
                department_id = departments_map.get(department_name)
                
                # Handle price
                price = row['Product Price']
                if pd.isna(price):
                    price = 0.0
                else:
                    try:
                        price = float(price)
                    except (ValueError, TypeError):
                        price = 0.0
                
                product = Product(
                    product_id=int(product_id),
                    name=str(row['Product Name']).strip(),
                    category_id_original=row['Product Category Id'],
                    department_id_original=row['Department Id'],
                    price=price,
                    status=str(row['Product Status']).strip(),
                    category_id=category_id,
                    department_id=department_id
                )
                
                session.add(product)
                products_added += 1
                
                # Commit in batches
                if products_added % 1000 == 0:
                    session.commit()
                    logger.info(f"Loaded {products_added} products...")
                    
            except Exception as e:
                logger.warning(f"Failed to load product {row.get('Product Card Id', 'unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"✅ Loaded {products_added} products")
    
    async def _load_orders(self, df, session):
        """Load order data"""
        # Get reference data mappings
        payment_types_map = {pt.name: pt.id for pt in session.query(PaymentType).all()}
        delivery_statuses_map = {ds.name: ds.id for ds in session.query(DeliveryStatus).all()}
        shipping_modes_map = {sm.name: sm.id for sm in session.query(ShippingMode).all()}
        order_statuses_map = {os.name: os.id for os in session.query(OrderStatus).all()}
        markets_map = {m.name: m.id for m in session.query(Market).all()}
        
        # Get unique orders
        orders_df = df[[
            'Order Id', 'Order Date (DateOrders)', 'order date (DateOrders)',
            'Customer Id', 'Type', 'Days for shipping (real)', 'Days for shipment (scheduled)',
            'Delivery Status', 'Late_delivery_risk', 'Category Id', 'Category Name',
            'Customer City', 'Customer Country', 'Customer State', 'Customer Zipcode',
            'Market', 'Order Region', 'Order Country', 'Order City', 'Order State',
            'Order Zipcode', 'Order Customer Id', 'Order Item Discount',
            'Order Item Discount Rate', 'Order Item Product Price', 'Order Item Profit Ratio',
            'Order Item Quantity', 'Sales', 'Order Item Total', 'Order Profit Per Order',
            'Order Status', 'Shipping Mode'
        ]].drop_duplicates(subset=['Order Id'])
        
        orders_added = 0
        
        for _, row in orders_df.iterrows():
            try:
                # Skip invalid records
                order_id = row['Order Id']
                if pd.isna(order_id) or order_id in ['XXXXXXXXX', '']:
                    continue
                
                # Parse order date
                order_date = None
                for date_col in ['Order Date (DateOrders)', 'order date (DateOrders)']:
                    if date_col in row and not pd.isna(row[date_col]):
                        try:
                            order_date = pd.to_datetime(row[date_col]).date()
                            break
                        except:
                            continue
                
                # Get reference IDs
                payment_type_id = payment_types_map.get(str(row['Type']).strip())
                delivery_status_id = delivery_statuses_map.get(str(row['Delivery Status']).strip())
                shipping_mode_id = shipping_modes_map.get(str(row['Shipping Mode']).strip())
                order_status_id = order_statuses_map.get(str(row['Order Status']).strip())
                market_id = markets_map.get(str(row['Market']).strip())
                
                # Handle numeric fields
                def safe_float(val, default=0.0):
                    try:
                        return float(val) if not pd.isna(val) else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(val, default=0):
                    try:
                        return int(val) if not pd.isna(val) else default
                    except (ValueError, TypeError):
                        return default
                
                order = Order(
                    order_id=int(order_id),
                    order_date=order_date,
                    customer_id=safe_int(row['Customer Id']),
                    days_for_shipping_real=safe_int(row['Days for shipping (real)']),
                    days_for_shipment_scheduled=safe_int(row['Days for shipment (scheduled)']),
                    late_delivery_risk=bool(row.get('Late_delivery_risk', 0)),
                    order_region=str(row.get('Order Region', '')).strip(),
                    order_country=str(row.get('Order Country', '')).strip(),
                    order_city=str(row.get('Order City', '')).strip(),
                    order_state=str(row.get('Order State', '')).strip(),
                    order_zipcode=str(row.get('Order Zipcode', '')).strip(),
                    sales=safe_float(row.get('Sales')),
                    order_profit_per_order=safe_float(row.get('Order Profit Per Order')),
                    payment_type_id=payment_type_id,
                    delivery_status_id=delivery_status_id,
                    shipping_mode_id=shipping_mode_id,
                    order_status_id=order_status_id,
                    market_id=market_id
                )
                
                session.add(order)
                orders_added += 1
                
                # Commit in batches
                if orders_added % 1000 == 0:
                    session.commit()
                    logger.info(f"Loaded {orders_added} orders...")
                    
            except Exception as e:
                logger.warning(f"Failed to load order {row.get('Order Id', 'unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"✅ Loaded {orders_added} orders")
    
    async def _load_order_items(self, df, session):
        """Load order items data"""
        order_items_added = 0
        
        for _, row in df.iterrows():
            try:
                # Skip invalid records
                order_id = row['Order Id']
                product_id = row['Product Card Id']
                
                if pd.isna(order_id) or pd.isna(product_id):
                    continue
                    
                if order_id in ['XXXXXXXXX', ''] or product_id in ['XXXXXXXXX', '']:
                    continue
                
                # Handle numeric fields
                def safe_float(val, default=0.0):
                    try:
                        return float(val) if not pd.isna(val) else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(val, default=0):
                    try:
                        return int(val) if not pd.isna(val) else default
                    except (ValueError, TypeError):
                        return default
                
                order_item = OrderItem(
                    order_id=int(order_id),
                    product_id=int(product_id),
                    quantity=safe_int(row.get('Order Item Quantity', 1)),
                    unit_price=safe_float(row.get('Order Item Product Price')),
                    discount=safe_float(row.get('Order Item Discount')),
                    discount_rate=safe_float(row.get('Order Item Discount Rate')),
                    profit_ratio=safe_float(row.get('Order Item Profit Ratio')),
                    total=safe_float(row.get('Order Item Total'))
                )
                
                session.add(order_item)
                order_items_added += 1
                
                # Commit in batches
                if order_items_added % 5000 == 0:
                    session.commit()
                    logger.info(f"Loaded {order_items_added} order items...")
                    
            except Exception as e:
                logger.warning(f"Failed to load order item for order {row.get('Order Id', 'unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"✅ Loaded {order_items_added} order items")
    
    async def _load_pdfs_to_mongodb(self) -> bool:
        """Load PDF documents into MongoDB"""
        try:
            pdf_dir = Path("../Document_Repository(dataco-global-policy-dataset)")
            
            if not pdf_dir.exists():
                logger.error(f"PDF directory not found: {pdf_dir}")
                return False
            
            pdf_files = list(pdf_dir.glob("*.pdf"))
            logger.info(f"📁 Found {len(pdf_files)} PDF files")
            
            if not pdf_files:
                logger.warning("No PDF files found")
                return True
            
            # Clear existing documents
            await self.db_manager.mongodb.delete_document(
                MongoDBCollections.POLICY_DOCUMENTS, 
                {}  # Delete all
            )
            
            successful_imports = 0
            
            for pdf_file in pdf_files:
                try:
                    # Extract text from PDF
                    text, page_count, file_size = self._extract_pdf_text(pdf_file)
                    
                    if text and len(text.strip()) > 50:
                        # Create policy document
                        policy_doc = PolicyDocument(
                            filename=pdf_file.name,
                            title=self._extract_title_from_filename(pdf_file.name),
                            content=self._clean_text(text),
                            content_type="policy",
                            file_size=file_size,
                            page_count=page_count,
                            word_count=len(text.split()),
                            categories=self._categorize_document(pdf_file.name),
                            tags=self._extract_tags(pdf_file.name, text),
                            department=self._extract_department(pdf_file.name),
                            region="Global",
                            status=DocumentStatus.INDEXED.value,
                            embeddings_status="pending"
                        )
                        
                        # Store in MongoDB
                        doc_id = await self.db_manager.store_document(
                            MongoDBCollections.POLICY_DOCUMENTS,
                            policy_doc.to_dict()
                        )
                        
                        # Create document chunks for RAG
                        await self._create_document_chunks(doc_id, text)
                        
                        successful_imports += 1
                        logger.info(f"✅ Processed: {pdf_file.name}")
                        
                    else:
                        logger.warning(f"⚠️ Skipped: {pdf_file.name} (insufficient content)")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {pdf_file.name}: {e}")
                    continue
            
            logger.info(f"✅ MongoDB documents loaded: {successful_imports}/{len(pdf_files)}")
            return successful_imports > 0
            
        except Exception as e:
            logger.error(f"❌ PDF loading failed: {e}")
            return False
    
    def _extract_pdf_text(self, pdf_path: Path) -> tuple:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                file_size = pdf_path.stat().st_size
                return text.strip(), page_count, file_size
                
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return None, 0, 0
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        return text.strip()
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract readable title from filename"""
        title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        title = re.sub(r'\bDataco\b', 'DataCo', title, flags=re.IGNORECASE)
        title = ' '.join(word.capitalize() for word in title.split())
        return title
    
    def _categorize_document(self, filename: str) -> List[str]:
        """Categorize document based on filename"""
        categories = []
        filename_lower = filename.lower()
        
        category_keywords = {
            'inventory': ['inventory', 'warehouse', 'storage'],
            'supplier': ['supplier', 'sourcing', 'procurement'],
            'quality': ['quality', 'qc', 'qa'],
            'logistics': ['logistics', 'transportation', 'shipping'],
            'risk': ['risk', 'security', 'safety'],
            'compliance': ['compliance', 'regulatory', 'trade'],
            'sustainability': ['sustainability', 'environment', 'green'],
            'operations': ['operations', 'process', 'management']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in filename_lower for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ['general']
    
    def _extract_tags(self, filename: str, content: str) -> List[str]:
        """Extract tags from filename and content"""
        tags = []
        
        # Tags from filename
        filename_tags = {
            'policy': 'policy' in filename.lower(),
            'procedure': 'procedure' in filename.lower(),
            'management': 'management' in filename.lower(),
            'global': 'global' in filename.lower(),
            'supply-chain': any(word in filename.lower() for word in ['supply', 'chain']),
        }
        
        tags.extend([tag for tag, present in filename_tags.items() if present])
        
        # Tags from content (first 1000 chars)
        content_sample = content[:1000].lower()
        content_tags = {
            'kpi': 'kpi' in content_sample,
            'process': 'process' in content_sample,
            'standard': 'standard' in content_sample,
            'requirement': 'requirement' in content_sample,
        }
        
        tags.extend([tag for tag, present in content_tags.items() if present])
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_department(self, filename: str) -> str:
        """Extract department from filename"""
        filename_lower = filename.lower()
        
        departments = {
            'operations': ['inventory', 'warehouse', 'operations', 'logistics'],
            'procurement': ['supplier', 'sourcing', 'procurement'],
            'quality': ['quality', 'qa', 'qc'],
            'finance': ['cost', 'finance', 'contract'],
            'compliance': ['compliance', 'regulatory', 'trade'],
            'hr': ['labor', 'diversity', 'inclusion'],
            'it': ['data', 'security', 'iot', 'technology'],
            'sustainability': ['sustainability', 'environment', 'circular']
        }
        
        for dept, keywords in departments.items():
            if any(keyword in filename_lower for keyword in keywords):
                return dept.title()
        
        return "General"
    
    async def _create_document_chunks(self, document_id: str, content: str):
        """Create text chunks for RAG"""
        chunk_size = 500
        chunk_overlap = 100
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            
            # Try to break at sentence boundary
            if end < len(content):
                last_period = content[max(start, end-100):end].rfind('.')
                if last_period != -1:
                    end = start + max(start, end-100) + last_period + 1
            
            chunk_content = content[start:end].strip()
            
            if chunk_content:
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    content=chunk_content,
                    start_position=start,
                    end_position=end,
                    word_count=len(chunk_content.split())
                )
                
                chunks.append(chunk.to_dict())
                chunk_index += 1
            
            start = end - chunk_overlap
        
        # Store chunks in MongoDB
        if chunks:
            await self.db_manager.mongodb.insert_many_documents(
                MongoDBCollections.DOCUMENT_CHUNKS,
                chunks
            )
    
    async def _print_summary(self):
        """Print loading summary"""
        try:
            # PostgreSQL statistics
            postgres_stats = {}
            tables = ['customers', 'products', 'orders', 'order_items', 'policy_documents']
            
            for table in tables:
                try:
                    count = await self.db_manager.execute_sql(f"SELECT COUNT(*) as count FROM {table}")
                    postgres_stats[table] = count[0]['count'] if count else 0
                except:
                    postgres_stats[table] = 0
            
            # MongoDB statistics
            mongodb_stats = {}
            collections = [
                MongoDBCollections.POLICY_DOCUMENTS,
                MongoDBCollections.DOCUMENT_CHUNKS
            ]
            
            for collection in collections:
                try:
                    stats = await self.db_manager.mongodb.get_collection_stats(collection)
                    mongodb_stats[collection] = stats['count']
                except:
                    mongodb_stats[collection] = 0
            
            # Print summary
            print("\n" + "="*60)
            print("📊 DUAL DATABASE LOADING SUMMARY")
            print("="*60)
            
            print("\n🐘 PostgreSQL (Structured Data):")
            for table, count in postgres_stats.items():
                print(f"   - {table}: {count:,}")
            
            print("\n🍃 MongoDB (Documents):")
            for collection, count in mongodb_stats.items():
                print(f"   - {collection}: {count:,}")
            
            # System health
            health = await self.db_manager.get_system_health()
            print(f"\n🏥 System Health: {health['overall'].upper()}")
            print(f"   - PostgreSQL: {health['postgres']['status']}")
            print(f"   - MongoDB: {health['mongodb']['status']}")
            
            print("\n✅ Dual database setup completed successfully!")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")

async def main():
    """Main function to load all data"""
    loader = DualDatabaseLoader()
    
    try:
        success = await loader.load_all_data()
        
        if success:
            print("\n🎉 All data loaded successfully into dual database system!")
            print("\n📋 Next steps:")
            print("   1. Run the test suite: python test_dual_database.py")
            print("   2. Start the FastAPI server: uvicorn app:app --reload")
            print("   3. Test the Text-to-SQL system with real data!")
        else:
            print("\n❌ Data loading failed. Check logs for details.")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the loader
    exit_code = asyncio.run(main())
    sys.exit(exit_code)