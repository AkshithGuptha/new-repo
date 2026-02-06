import React, { useState } from "react";
import { motion } from "framer-motion";
import "./Hero.css";

const Hero = () => {
  const [answered, setAnswered] = useState(false);
  const [noPos, setNoPos] = useState({ x: 0, y: 0 });
  const [sending, setSending] = useState(false);

  const moveNoButton = () => {
    const x = (Math.random() - 0.5) * 600;
    const y = (Math.random() - 0.5) * 400;
    setNoPos({ x, y });
  };

  const handleYes = async () => {
    setSending(true);
    try {
      // Call backend API to send email
      const response = await fetch("http://localhost:3001/api/valentine-yes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          timestamp: new Date().toLocaleString(),
        }),
      });
      
      if (response.ok) {
        setAnswered(true);
      } else {
        console.error("Failed to send message");
        setAnswered(true);
      }
    } catch (error) {
      console.error("Error:", error);
      setAnswered(true);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="hero">
      <div className="card">
        {!answered ? (
          <>
            <h1>Anvitha, will you be my Valentine? Ì≤å</h1>

            <motion.p
              className="subtitle"
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              I really like you... Ì≤ï
            </motion.p>

            <div className="btns">
              <motion.button
                className="yes"
                onClick={handleYes}
                disabled={sending}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                {sending ? "Sending..." : "Yes ‚ù§Ô∏è"}
              </motion.button>

              <motion.button
                className="no"
                onMouseEnter={moveNoButton}
                onClick={moveNoButton}
                style={{
                  transform: `translate(${noPos.x}px, ${noPos.y}px)`,
                }}
                transition={{ type: "spring", stiffness: 500, damping: 20 }}
              >
                No
              </motion.button>
            </div>
          </>
        ) : (
          <div className="success">
            <motion.h1
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 100 }}
            >
              You made me the happiest! ÌæâÌ≤ï
            </motion.h1>

            <motion.p
              className="msg"
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              Let's celebrate this together, Anvitha! Ìºπ‚ú®
            </motion.p>

            <motion.img
              src="https://media.giphy.com/media/3oz8xAFtqoOUUrsh7W/giphy.gif"
              alt="celebration"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Hero;
