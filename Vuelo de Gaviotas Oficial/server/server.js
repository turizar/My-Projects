const express = require("express");
const path = require("path");

const app = express();
const port = 3000;

// Ruta absoluta a la carpeta public
app.use(express.static(path.join(__dirname, "../public")));

app.listen(port, () => {
  console.log(`Servidor corriendo en http://localhost:${port}`);
});