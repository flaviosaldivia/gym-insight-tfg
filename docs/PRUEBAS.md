# Plan de pruebas de Gym Insight

## Pruebas automatizadas

Ejecutar desde la raíz:

```bash
pip install -r backend/requirements.txt
pytest -q backend/tests
python -m compileall -q backend/app backend/scripts
```

Las pruebas comprueban normalización de fechas/correos y completado de días sin registros mediante Pandas. GitHub Actions ejecuta estas pruebas y compila el frontend en cada `push` o `pull_request` hacia `main`/`master`.

## Pruebas funcionales manuales

| ID | Caso | Resultado esperado |
|---|---|---|
| TF-01 | Abrir `/api/health` | JSON con `status: ok` |
| TF-02 | Abrir `/docs` | Documentación OpenAPI visible |
| TF-03 | Cargar seed | 120 socios y datos relacionados |
| TF-04 | Abrir dashboard | KPIs y gráficos consultan API |
| TF-05 | Cambiar período | Tarjetas y series se actualizan |
| TF-06 | Buscar socio | Resultados filtrados por nombre/email |
| TF-07 | Consultar membresías | Plan, estado y vencimiento visibles |
| TF-08 | Consultar alertas | Membresías próximas a vencer listadas |
| TF-09 | Importar CSV correcto | Registros nuevos insertados |
| TF-10 | Importar email duplicado | Duplicado reportado y no reinsertado |
| TF-11 | Importar CSV sin columna obligatoria | Error descriptivo |

## Criterios de aceptación

- Los conteos deben coincidir con un conjunto de prueba conocido.
- Los ingresos deben sumar solamente pagos en estado `cobrado` dentro del período.
- Los filtros temporales deben aplicarse consistentemente.
- Los registros duplicados o inválidos no deben alterar los indicadores.
- Tarjetas y gráficos deben corresponder al mismo período y conjunto de datos.

Las reglas de bajas y renovaciones son aproximaciones del prototipo y requieren validación de negocio antes de considerarse definitivas.
