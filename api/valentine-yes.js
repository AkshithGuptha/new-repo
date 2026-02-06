import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { timestamp } = req.body;

    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: process.env.EMAIL_USER,
      subject: 'í¾‰ Anvitha said YES to your Valentine proposal!',
      html: `
        <h2>She said YES! í²•</h2>
        <p>Anvitha accepted your Valentine proposal!</p>
        <p><strong>Time:</strong> ${timestamp}</p>
        <p>Congratulations! ï¿½ï¿½</p>
      `,
    });

    res.status(200).json({ success: true, message: 'Email sent successfully!' });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
}
