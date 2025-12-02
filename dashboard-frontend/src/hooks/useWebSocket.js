export default function useWebSocket(url, onMessage) {
  const ws = new WebSocket(url);

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    onMessage(data);
  };

  return ws;
}
