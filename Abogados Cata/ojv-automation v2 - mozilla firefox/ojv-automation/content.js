(function () {
  if (!location.href.includes("oficinajudicialvirtual.pjud.cl")) return;

  const wait = ms => new Promise(res => setTimeout(res, ms));

  function injectUploadButton() {
    if (document.getElementById("rut-upload-button")) return;

    const button = document.createElement("button");
    button.id = "rut-upload-button";
    button.innerText = "📁 Subir CSV con RUTs";
    Object.assign(button.style, {
      position: "fixed",
      top: "10px",
      right: "10px",
      zIndex: 10000,
      padding: "10px",
      background: "#0074D9",
      color: "white",
      border: "none",
      borderRadius: "5px",
      cursor: "pointer"
    });
    document.body.appendChild(button);

    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".csv";
    input.style.display = "none";
    document.body.appendChild(input);

    button.addEventListener("click", () => input.click());

    input.addEventListener("change", async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      try {
        const text = await file.text();
        const ruts = text
          .split(/\r?\n/)
          .map(line => line.trim().replace(/\s+/g, ''))
          .filter(line => line.length > 0 && /^[0-9]+-[0-9kK]$/.test(line));

        if (ruts.length === 0) {
          alert("❌ No se encontraron RUTs válidos en el archivo CSV.");
          return;
        }

        console.log("📥 RUTs cargados:", ruts);
        localStorage.setItem("rut_list", JSON.stringify(ruts));

        goToConsultaUnificada();
        await wait(3000);
        goToBúsquedaporRutPersonaJurídica();
        await wait(5000);
        automateRutSearch();

      } catch (error) {
        alert("❌ No se pudo leer el archivo CSV.");
        console.error(error);
      }
    });
  }

  function goToConsultaUnificada() {
    const link = [...document.querySelectorAll("a")].find(el => el.textContent.includes("Consulta Unificada"));
    if (link) {
      link.click();
    } else {
      console.error("❌ No se encontró el enlace a 'Consulta Unificada'");
    }
  }

  function goToBúsquedaporRutPersonaJurídica() {
    const link = [...document.querySelectorAll("a")].find(el => el.textContent.includes("Búsqueda por Rut Persona Jurídica"));
    if (link) {
      link.click();
    } else {
      console.error("❌ No se encontró el enlace a 'Búsqueda por Rut Persona Jurídica'");
    }
  }

    async function automateRutSearch() {
    const ruts = JSON.parse(localStorage.getItem("rut_list") || "[]");
    if (ruts.length === 0) return;

    console.log("Automatizando búsqueda para RUTs:", ruts);

    // Wait for page readiness
    await wait(3000);

    // Navigate to "Búsqueda por Rut Persona Jurídica"
    const btnRutJuridica = [...document.querySelectorAll("a")].find(a => a.textContent.includes("Búsqueda por Rut Persona Jurídica"));
    if (!btnRutJuridica) {
        alert("No se encontró el enlace a 'Búsqueda por Rut Persona Jurídica'.");
        return;
    }
    btnRutJuridica.click();
    await wait(3000);

    let allData = [];
    let isFirstRut = true;

    for (const rut of ruts) {
        console.log(`Buscando RUT: ${rut}`);

        const [rutNum, rutDv] = rut.split("-");
        const inputRut = document.querySelector("#rutJur");
        const inputDv = document.querySelector("#dvJur");

        if (!inputRut || !inputDv) {
        alert("No se encontraron los campos para ingresar RUT en la página.");
        return;
        }
        inputRut.value = rutNum;
        inputDv.value = rutDv;

        const btnBuscar = document.querySelector("#btnConConsultaJur");
        if (!btnBuscar) {
        alert("No se encontró el botón de búsqueda en la página.");
        return;
        }
        btnBuscar.click();
        await wait(3000); // wait for results to load

        let page = 1;

        while (true) {
        const resultTable = document.querySelector("#dtaTableDetalleJuridica");
        if (!resultTable) {
            alert(`❌ No se encontró la tabla en la página ${page} para el RUT ${rut}.`);
            break;
        }

        const tableRows = [...resultTable.rows];
        const isFirstPage = page === 1;

        // Remove footer row (pagination)
        const trimmedRows = tableRows.slice(0, -1);

        // Extract header (from first row)
        const header = [...trimmedRows[0].cells].map(cell => cell.innerText.trim());

        // Extract data rows (excluding header)
        const dataRows = trimmedRows.slice(1).map(row =>
            [...row.cells].map(cell => cell.innerText.trim())
        );

        // Date filtering
        const dateColIndex = 4; // Adjust if needed
        const today = new Date();
        const oneYearAgo = new Date(today);
        oneYearAgo.setFullYear(today.getFullYear() - 1);

        function parseDate(str) {
            const parts = str.split('/');
            if (parts.length === 3) {
            return new Date(parts[2], parts[1] - 1, parts[0]);
            }
            const d = new Date(str);
            return isNaN(d) ? null : d;
        }

        const filteredDataRows = dataRows.filter(row => {
            const dateStr = row[dateColIndex];
            const date = parseDate(dateStr);
            if (!date) return false;
            return date >= oneYearAgo;
        });

        // Append data to allData, include header only once (first RUT, first page)
        if (isFirstRut && isFirstPage) {
            allData.push(header, ...filteredDataRows);
        } else {
            allData.push(...filteredDataRows);
        }

        console.log(`✅ Página ${page} capturada para RUT ${rut}.`);

        // Check if next page available
        const nextBtn = document.querySelector('#sigId');
        if (!nextBtn || nextBtn.classList.contains("disabled") || nextBtn.hasAttribute("aria-disabled")) {
            console.log(`ℹ️ No hay más páginas para RUT ${rut}.`);
            break;
        }

        nextBtn.click();
        page++;
        await wait(3000); // wait for next page load
        }

        // After finishing current RUT, click Limpiar (Clear)
        const btnLimpiar = document.querySelector("#btnLimpiarJur");
        if (btnLimpiar) {
        btnLimpiar.click();
        await wait(1500); // give some time to reset form
        } else {
        console.warn("No se encontró botón Limpiar.");
        }

        isFirstRut = false; // after first RUT, header is already saved
    }

    // Export all accumulated data in one Excel file
    const ws = XLSX.utils.aoa_to_sheet(allData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Resultados");

    // Sanitize filename to remove dashes and avoid problems
    //   const fileName = `resultado_todos_${Date.now()}.xlsx`;
    const fileName = `output.xlsx`;
    XLSX.writeFile(wb, fileName);

    console.log(`✅ Archivo exportado como ${fileName}`);
    }

  injectUploadButton();

})();
