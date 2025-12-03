// simple linear interpolation smoothing between points
export function interpolatePath(points, steps = 5) {
  // points: [[lat, lon], ...]
  const out = [];
  for (let i = 0; i < points.length - 1; i++) {
    const [aLat, aLon] = points[i];
    const [bLat, bLon] = points[i + 1];
    out.push([aLat, aLon]);
    for (let s = 1; s < steps; s++) {
      const t = s / steps;
      out.push([aLat + (bLat - aLat) * t, aLon + (bLon - aLon) * t]);
    }
  }
  if (points.length) out.push(points[points.length - 1]);
  return out;
}
