const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const redis = require('redis');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Version для проверки совместимости
const BACKEND_VERSION = process.env.BACKEND_VERSION || 'v3';
const PORT = process.env.PORT || 3000;

// Redis клиент
const redisClient = redis.createClient({
    socket: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379
    }
});

redisClient.on('error', err => console.log('Redis Error:', err));
redisClient.on('connect', () => console.log('Connected to Redis'));

// Подключаемся к Redis
(async () => {
    await redisClient.connect();
})();

// API endpoints
app.use(express.json());

app.get('/api/version', (req, res) => {
    res.json({ 
        version: BACKEND_VERSION,
        timestamp: new Date().toISOString()
    });
});

app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok',
        version: BACKEND_VERSION,
        redis: redisClient.isReady ? 'connected' : 'disconnected'
    });
});

// WebSocket handling
io.on('connection', (socket) => {
    console.log('New client connected');
    
    socket.on('message', async (msg) => {
        // Сохраняем в Redis
        const message = {
            ...msg,
            id: Date.now().toString()
        };
        
        await redisClient.lPush('messages', JSON.stringify(message));
        await redisClient.lTrim('messages', 0, 99); // Храним последние 100
        
        // Отправляем всем клиентам
        io.emit('message', message);
    });
    
    socket.on('get-history', async () => {
        const messages = await redisClient.lRange('messages', 0, -1);
        const parsed = messages.map(m => JSON.parse(m)).reverse();
        socket.emit('history', parsed);
    });
    
    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

server.listen(PORT, () => {
    console.log(`Backend ${BACKEND_VERSION} running on port ${PORT}`);
});