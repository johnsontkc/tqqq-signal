// netlify/functions/yahoo-proxy.js
exports.handler = async function(event, context) {
  const ticker = event.queryStringParameters.ticker || 'TQQQ';
  const range = event.queryStringParameters.range || '1y';
  const interval = event.queryStringParameters.interval || '1d';
  
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval}&range=${range}&includePrePost=false`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
      }
    });
    
    const data = await response.json();
    
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed fetching data' })
    };
  }
};
