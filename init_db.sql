CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username TEXT,
    registered_at TIMESTAMP DEFAULT NOW(),
    is_premium BOOL DEFAULT FALSE,
    premium_until TIMESTAMP,
    requests_left INT DEFAULT 3,
    bonus_points INT DEFAULT 0,
    invite_code TEXT,
    referred_by TEXT,
    last_request DATE
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    plan TEXT,
    amount NUMERIC,
    success BOOL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    inviter_id BIGINT,
    friend_id BIGINT,
    bonus_points INT,
    time TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bonds (
    id SERIAL PRIMARY KEY,
    isin TEXT,
    issuer TEXT,
    name TEXT,
    type TEXT,
    currency TEXT,
    coupon_rate NUMERIC,
    yield_to_maturity NUMERIC,
    maturity_date DATE,
    rating TEXT,
    url TEXT
);
