module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        cyberBg: "#071226",
        neonPink: "#ff2d95",
        neonCyan: "#3de3f2",
        neonPurple: "#a048ff"
      },
      boxShadow: {
        neon: "0 6px 30px rgba(61,227,242,0.08), 0 0 20px rgba(160,72,255,0.06)"
      }
    }
  },
  plugins: []
};
