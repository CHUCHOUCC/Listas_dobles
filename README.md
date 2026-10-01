# FlipBook: animador cuadro por cuadro con Listas Dobles

**Curso:** Estructuras de Datos, UCC
**Lenguaje:** Python 3 (POO) · **Frontend:** tkinter

## Caso de estudio

Las apps de animación tipo **FlipaClip** funcionan como un cuaderno de dibujos animados.
La animación es una secuencia de **cuadros (frames)** y el usuario dibuja uno a la vez.
Con eso puede:

- avanzar y retroceder entre cuadros,
- insertar un cuadro nuevo o duplicado **en medio** de la secuencia,
- eliminar o reordenar cuadros,
- ver el cuadro anterior y el siguiente semitransparentes (**papel cebolla / onion skin**) para calcar el movimiento,
- reproducir la animación hacia adelante y **en reversa**.

Todas esas operaciones son exactamente las ventajas de una **lista doblemente enlazada**:
recorrido en ambas direcciones e inserción y eliminación en cualquier posición sin mover los demás elementos.

## ¿Dónde se usa cada lista?

```
Animation ──(Lista DOBLE)──> Frame ──(Lista SIMPLE)──> Stroke ──(Lista SIMPLE)──> Point
```

| Estructura | Guarda | Por qué |
|---|---|---|
| `DoublyLinkedList` | los cuadros de la animación | se navega en ambos sentidos, se reproduce en reversa, el onion skin usa `prev` y `next`, y se inserta, borra o reordena en medio |
| `SinglyLinkedList` | los trazos de un cuadro y los puntos de un trazo | solo se agregan al final y se recorren de inicio a fin |

El "cabezal" de la animación (`Animation.current`) es una **referencia a un nodo**.
Pasar al siguiente cuadro es `current = current.next`, y volver es `current = current.prev`.

## Restricción de bajo nivel

No se usan arrays ni métodos de colecciones del lenguaje para guardar los datos.
Eso excluye `list`, `tuple`, `dict`, `[]`, `len()`, `.append()` de Python, `range()`, `split` y `join`.
Todo vive en nodos enlazados creados a mano, y los tamaños se llevan con contadores propios.
Hasta la paleta de colores de la interfaz es una lista simple.

## Operaciones y complejidad

| Acción en la app | Método de la lista | Complejidad |
|---|---|---|
| Cuadro siguiente / anterior | `current.next` / `current.prev` | O(1) |
| `+ New` / `Duplicate` | `insert_after(node, value)` | O(1) (duplicate copia los trazos) |
| `Delete` | `remove(node)`: no recorre, gracias a `prev` | O(1) |
| `Move left` / `Move right` | `swap_with_next(node)`: solo re-enlaza punteros | O(1) |
| Clic en la línea de tiempo | `get_at(index)`: recorre desde la cabeza o desde la cola, según cuál esté más cerca | O(n/2) |
| `Reverse` (reproducir al revés) | recorrido con `prev` desde la cola | O(1) por cuadro |
| `Undo` (último trazo) | `SinglyLinkedList.remove_last()`: en lista simple hay que recorrer | O(n) |

La última fila compara las dos estructuras: en la lista simple, quitar el último elemento obliga a recorrer toda la lista.
En la doble, `remove(node)` es directo.

## Cómo ejecutar

```bash
python app.py
```

Se necesita Python 3.8 o superior. tkinter ya viene con Python en Windows y macOS.
En Linux puede hacer falta instalarlo con `sudo apt install python3-tk`.
Los tres archivos `.py` deben estar en la misma carpeta.

## Controles

- **Dibujar:** clic y arrastrar sobre el lienzo. Se elige color, borrador y grosor del pincel en la barra superior.
- **Undo / Clear frame:** deshacer el último trazo o limpiar el cuadro.
- **|< < > >|:** ir al primer cuadro, al anterior, al siguiente o al último.
- **+ New / Duplicate / Delete / Move left / Move right:** editar la secuencia de cuadros.
- **Play / Reverse / Stop**, **FPS**, **Loop**, **Onion skin:** controles de reproducción.
- **Línea de tiempo:** clic en una miniatura para saltar a ese cuadro.
- **Atajos:** `←` `→` para navegar, `Espacio` para play/stop, `Ctrl+Z` para deshacer.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `linked_lists.py` | `SingleNode`, `SinglyLinkedList`, `DoubleNode`, `DoublyLinkedList` |
| `animation.py` | modelo del dominio: `Point`, `Stroke`, `Frame`, `Animation` |
| `app.py` | interfaz gráfica: `CanvasRenderer` (dibuja recorriendo las listas) y `FlipbookApp` (ventana y eventos) |
