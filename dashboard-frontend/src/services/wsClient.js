import ReconnectingWebSocket from "reconnecting-websocket";

export function createWsClient(url) {
  const options = {
    maxRetries: 9999,
    connectionTimeout: 4000,
    reconnectInterval: 1000
  };
  const rws = new ReconnectingWebSocket(url, [], options);
  return rws;
}
