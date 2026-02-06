import express from 'express';
import cors from 'cors';
import nodemailer from 'nodemailer';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Configure email service (using Gmail or your email provider)
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

app.post('/api/valentine-yes', async (req, res) => {
  try {
    const { timestamp } = req.body;

    // Send email to your address
    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: process.env.EMAIL_USER,
      subject: 'í¾‰ Anvitha said YES to your Valentine proposal!',
      html: `
        <h2>She said YES! í²•</h2>
        <p>Anvitha accepted your Valentine proposal!</p>
        <p><strong>Time:</strong> ${timestamp}</p>
        <p>Congratulations! í¾‰</p>
      `,
    });

    res.json({ success: true, message: 'Email sent successfully!' });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
