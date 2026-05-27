Reorganize Simulation Outputs to /results/ - Task Checklist
[ ] Set up directory creation for results/data/txt, results/data/csv, results/img/png, results/img/svg
[ ] Disable auto-cleanup of simulation .txt files
[ ] Implement exporting simulation data (DC, AC, CMRR, Zout, Transients) to .txt in results/data/txt/
[ ] Implement exporting simulation data (DC, AC, CMRR, Zout, Transients) to .csv in results/data/csv/
[ ] Save plots to results/img/png/
[ ] Save plots to results/img/svg/
[ ] Modify simulate_instrampl.py
[ ] Create results subdirectories
[ ] Create subdirectorio de modelos importados en bruto desde PSpice, Tina u otros, en su raw format
[ ] Create subdirectorio de modelos importados desde PSpice, Tina u otros, y traducidos a ngspice
[ ] Los modelos creados (ya en formato ngspice) deben pasar a un subdirectorio de modelos creados
[ ] Los modelos importados en bruto deben pasar a un subdirectorio de modelos importados en bruto
[ ] Update netlists, data loading, and disable cleanup
[ ] Se deben crear archivos en python que realicen en ngspice las siguientes simulaciones:
[ ] Puntos de Trabajo
[ ] Análisis DC
[ ] Análisis de Acoplo AC
[ ] Análisis de Respuesta en frecuencia: ganancia en dB
[ ] Análisis de Respuesta en frecuencia: desfase en radianes
[ ] Análisis de Respuesta en frecuencia: límite de estabilidad
[ ] Análisis de Respuesta en frecuencia: productos de ancho de banda
[ ] Análisis de Impedancias en AC
[ ] Análisis de Impedancias en DC
[ ] Análisis de polos y zeros
[ ] Análisis transitorios en una buena variedad de frecuencias, habiendo corrido ya un número de periodos suficiente para estar seguros de lo que realmente ocurre (si T es el período, queremos ver que pasa entre t_i := 95T y t_f := 100T)
[ ] Export todos los resultados tanto a TXT como a CSV
[ ] Save plots as both PNG and SVG under results/img/
[ ] Modify simulate_superopamp.py
[ ] Create results subdirectories
[ ] Update netlists, data loading, and disable cleanup
[ ] Export DC, AC, and Transient results as CSV
[ ] Save plots as both PNG and SVG under results/img/
[ ] Modify simulate_comparison.py
[ ] Update netlists and data loading
[ ] Disable deletion of individual .txt files
[ ] Output consolidated comparison CSVs to results/data/csv/
[ ] Save comparison plots to results/img/png/ and results/img/svg/
[ ] Run simulations and verify folders
[ ] Run simulate_characterization.py
[ ] Verify that /results has the complete set of .txt, .csv, .png, and .svg files
[ ] Run other simulation scripts to ensure absolute correctness and sync
[ ] Necesitamos los circuitos en formato LaTeX
[ ] ¿Podemos generar el esquemático de KiCAD?
[ ] Generar Documentación (Documento md que integre los datos y las imáquenes, tanto como los circuitos)