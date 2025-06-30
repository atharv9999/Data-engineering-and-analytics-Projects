CREATE TABLE sales(
    sale_id SERIAL PRIMARY KEY,                         -- Unique sale ID
    sale_date TIMESTAMP NOT NULL DEFAULT NOW(),         -- Date of sale
    customer_id INT NOT NULL,                           -- Foreign key (customer)
    product_id INT NOT NULL,                            -- Foreign key (product)
    store_id INT NOT NULL,                              -- Foreign key (store)
    quantity INT CHECK (quantity > 0),                  -- Quantity sold
    unit_price NUMERIC(10, 2) NOT NULL,                 -- Price per unit
    discount NUMERIC(5, 2) DEFAULT 0.0,                 -- Discount on sale
    total_amount NUMERIC(12, 2) NOT NULL,               -- Total = (qty * unit_price - discount)
    payment_type VARCHAR(20) CHECK 
	(payment_type IN ('Cash', 'Card', 'UPI', 'Wallet')),
    status VARCHAR(20) DEFAULT 'Completed',             -- Completed, Returned, Cancelled
    remarks TEXT,                                       -- Any remarks or notes
    -- CDC column based on Timestamp
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- Used for CDC / incremental loads
);