import { motion } from "framer-motion";

interface ShiningTextProps {
  text: string;
  className?: string;
}

export function ShiningText({ text, className }: ShiningTextProps) {
  return (
    <motion.span
      className={className}
      style={{
        background: "linear-gradient(110deg, #333333 25%, #F56B00 50%, #333333 75%)",
        backgroundSize: "200% 100%",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        backgroundClip: "text",
        fontSize: "0.875rem",
      }}
      initial={{ backgroundPosition: "200% 0" }}
      animate={{ backgroundPosition: "-200% 0" }}
      transition={{
        repeat: Infinity,
        duration: 2,
        ease: "linear",
      }}
    >
      {text}
    </motion.span>
  );
}
