export default function NeonCard({ children, className = "" }) {
  return (
    <div className={`bg-[#07102a] p-4 rounded-xl border border-white/6 shadow-neon ${className}`}>
      {children}
    </div>
  );
}
