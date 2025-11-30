from sqlalchemy import DDL, event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL



engine = create_async_engine(DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)



VIEWS_AND_TRIGGERS_SQL = [
    # Представление для списка книг
    "DROP VIEW IF EXISTS vw_books_list;",
    """
    CREATE VIEW vw_books_list AS
    SELECT book_id, title, quantity, price
    FROM books;
    """,
    
    # Подробное представление книг
    "DROP VIEW IF EXISTS vw_books_detailed;",
    """
    CREATE VIEW vw_books_detailed AS
    SELECT 
        b.book_id,
        b.title,
        a.full_name AS author,
        t.name AS topic,
        l.name AS library_name,
        b.quantity,
        b.price
    FROM books b
    JOIN authors a ON b.author_id = a.author_id
    JOIN topics t ON b.topic_id = t.topic_id
    JOIN libraries l ON b.library_id = l.library_id;
    """,
    
    # Статистика по библиотекам
    "DROP VIEW IF EXISTS vw_library_stats;",
    """
    CREATE VIEW vw_library_stats AS
    SELECT 
        l.name AS library_name,
        COUNT(b.book_id) AS total_books,
        SUM(b.quantity) AS total_copies,
        SUM(b.quantity * b.price) AS total_value
    FROM libraries l
    LEFT JOIN books b ON l.library_id = b.library_id
    GROUP BY l.library_id, l.name
    HAVING COUNT(b.book_id) > 0;
    """,
    
    # Статистика по авторам
    "DROP VIEW IF EXISTS vw_author_stats;",
    """
    CREATE VIEW vw_author_stats AS
    SELECT 
        a.full_name AS author_name,
        COUNT(b.book_id) AS total_books,
        SUM(b.quantity) AS total_copies,
        AVG(b.price) AS avg_price
    FROM authors a
    LEFT JOIN books b ON a.author_id = b.author_id
    GROUP BY a.author_id, a.full_name
    HAVING COUNT(b.book_id) > 0;
    """,
    
    # Активные подписки
    "DROP VIEW IF EXISTS vw_active_subscriptions;",
    """
    CREATE VIEW vw_active_subscriptions AS
    SELECT 
        s.subscription_id,
        r.full_name AS reader_name,
        b.title AS book_title,
        l.name AS library_name,
        s.issue_date,
        s.return_date,
        s.deposit
    FROM subscriptions s
    JOIN readers r ON s.reader_id = r.reader_id
    JOIN books b ON s.book_id = b.book_id
    JOIN libraries l ON s.library_id = l.library_id
    WHERE s.return_date IS NULL;
    """,
    
    # Удаление существующих триггеров и функций
    "DROP TRIGGER IF EXISTS trg_decrease_quantity ON subscriptions;",
    "DROP FUNCTION IF EXISTS decrease_book_quantity();",
    "DROP TRIGGER IF EXISTS trg_increase_quantity ON subscriptions;",
    "DROP FUNCTION IF EXISTS increase_book_quantity();",
    
    # Триггер для уменьшения количества книг при выдаче
    """
    CREATE OR REPLACE FUNCTION decrease_book_quantity()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE books
        SET quantity = quantity - 1
        WHERE book_id = NEW.book_id AND quantity > 0;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """,
    
    """
    CREATE TRIGGER trg_decrease_quantity
    AFTER INSERT ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION decrease_book_quantity();
    """,
    
    # Триггер для увеличения количества книг при возврате
    """
    CREATE OR REPLACE FUNCTION increase_book_quantity()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE books
        SET quantity = quantity + 1
        WHERE book_id = OLD.book_id;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """,
    
    """
    CREATE TRIGGER trg_increase_quantity
    AFTER DELETE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION increase_book_quantity();
    """
]

async def create_views_and_triggers():
    """Асинхронное создание представлений и триггеров"""
    async with Session() as session:
        try:
            for i, sql in enumerate(VIEWS_AND_TRIGGERS_SQL):
                try:
                    await session.execute(text(sql))
                    print(f"✅ Executed SQL command {i+1}/{len(VIEWS_AND_TRIGGERS_SQL)}")
                except Exception as e:
                    # Игнорируем ошибки "не существует" для DROP команд
                    if "DROP" in sql and "does not exist" in str(e):
                        print(f"ℹ️  Ignoring DROP error for non-existent object: {sql.split()[2]}")
                        continue
                    else:
                        print(f"❌ Error executing SQL command {i+1}: {e}")
                        print(f"SQL: {sql}")
                        raise
            
            await session.commit()
            print("✅ Views and triggers created successfully!")
        except Exception as e:
            print(f"❌ Error creating views and triggers: {e}")
            await session.rollback()
            raise