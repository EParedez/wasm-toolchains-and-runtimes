# Zig + Wasmtime: memoria acotada en WASI

Ejemplo reproducible para el caso práctico del artículo sobre WebAssembly. Lee
hasta 32 KiB de la entrada estándar, convierte letras ASCII a mayúsculas en el
mismo búfer y escribe el resultado. La lógica de procesamiento no solicita
memoria dinámica; el búfer de 32 KiB forma parte de la memoria lineal del módulo.
Esto **no** fija la memoria total que utiliza Wasmtime.

## Versiones

- Zig 0.13.0
- Wasmtime 50.0.0
- WASI Preview 1 (`wasm32-wasi`)

Las versiones están fijadas en el workflow de GitHub Actions. El tamaño del
binario se informa en cada ejecución de CI; no se supone un tamaño fijo.

## Compilar y ejecutar

```sh
zig build-exe processor.zig -target wasm32-wasi -O ReleaseSmall
printf '%s' '{"event": "user_login", "status": "ok"}' | wasmtime run -C cache=n processor.wasm
python3 tests/integration.py
```

Salida esperada para el `printf` anterior:

```text
Procesados 39 bytes en memoria fija:
{"EVENT": "USER_LOGIN", "STATUS": "OK"}
```

El límite incluye cualquier salto de línea recibido por `stdin`. Una entrada
de 32,768 bytes se acepta; una de 32,769 bytes se rechaza con `StreamTooLong`.
La transformación es ASCII: no modifica caracteres Unicode fuera de ASCII.

## Qué comprueba CI

- Compilación del módulo con la versión fijada de Zig.
- Ejecución en la versión fijada de Wasmtime.
- Salida para entrada vacía y un payload JSON.
- Comportamiento en el límite y un byte por encima.
- Tamaño real del archivo `.wasm` generado.

El workflow no pretende medir latencia, memoria residente ni densidad de
instancias. Esas métricas requieren un benchmark separado con entorno y carga
documentados.
