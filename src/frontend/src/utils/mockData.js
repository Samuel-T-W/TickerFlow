import { format, subMinutes } from 'date-fns';

const TECH_TICKERS = [
    'AAPL', 'NVDA', 'GOOGL', 'META', 'AMZN', 'MSFT', 'TSLA', 'AMD', 'INTC', 'QCOM',
    'CSCO', 'NFLX', 'ADBE', 'CRM', 'TXN', 'AVGO', 'ORCL', 'IBM', 'PYPL', 'UBER',
    'ABNB', 'PLTR', 'SNOW', 'ZM', 'DOCU', 'WDAY', 'TEAM', 'ADSK', 'PANW', 'FTNT'
];

// Helper to generate random walk data
const generateIntradayData = (startPrice, points) => {
    const data = [];
    let currentPrice = startPrice;
    const now = new Date();

    // 1-minute intervals
    for (let i = points; i >= 0; i--) {
        const time = subMinutes(now, i); // Data every 1 minute
        // Increase volatility for "spiky" look
        const change = (Math.random() - 0.5) * 3; // Random change between -1.5 and 1.5
        currentPrice += change;

        // Ensure price doesn't go below 1
        if (currentPrice < 1) currentPrice = 1;

        data.push({
            time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            price: parseFloat(currentPrice.toFixed(2)),
            vwap: parseFloat((currentPrice + (Math.random() - 0.5) * 2).toFixed(2)), // Mock VWAP with noise
            ma: parseFloat((currentPrice + (Math.random() - 0.5) * 4).toFixed(2)), // Mock MA with more noise
        });
    }
    return data;
};

export const generateMockData = () => {
    return TECH_TICKERS.map((ticker, index) => {
        const startPrice = Math.random() * 100 + 50; // Random start price between 50 and 150

        // Vary data length: 
        // First 5 stocks have short history (e.g., 30 mins = 30 points)
        // Rest have full day (e.g., 390 points for 6.5 hours)
        const points = index < 5 ? 30 : 390;

        const data = generateIntradayData(startPrice, points);
        const prices = data.map(d => d.price);
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const latestPrice = prices[prices.length - 1];

        return {
            ticker,
            data,
            stats: {
                latest: latestPrice,
                high: maxPrice,
                low: minPrice,
            }
        };
    });
};

export const MOCK_DATA = generateMockData();
