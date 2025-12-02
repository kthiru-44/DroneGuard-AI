module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5fbff",
          100: "#e6f5ff",
          500: "#0ea5a4",
          700: "#0b7285"
        },
        ui: {
          50: "#f8fafc",
          100: "#eef2f7",
        }
      },
      boxShadow: {
        glass: "0 8px 30px rgba(2,6,23,0.08)"
      }
    }
  },
  plugins: []
};
