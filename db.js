const { Pool } = require('pg');

const pool = new Pool({
    host: 'c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',
    database: 'd1ghlt1k1v7p1b',
    user: 'u9re3c1av09l6a',
    password: 'p997b68e88358721ebf42927556296b51b51c6f34238fd8dc1e6f231dc708d4d6',
    port: 5432,
});

module.exports = pool;
