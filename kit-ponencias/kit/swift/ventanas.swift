// ventanas: monitores y ventanas de Zoom visibles, para que el kit sepa qué grabar.
//   DISPLAY|uuid|x,y,ancho,alto (puntos, origen arriba-izq. global)|escala (2 = Retina)|main=true/false
//   WINDOW|id|título|x,y,ancho,alto|layer
import CoreGraphics
import ColorSync
import Foundation

var n: UInt32 = 0
CGGetActiveDisplayList(0, nil, &n)
var ids = [CGDirectDisplayID](repeating: 0, count: Int(n))
CGGetActiveDisplayList(n, &ids, &n)
for d in ids {
  let b = CGDisplayBounds(d)
  var escala = 1.0
  if let m = CGDisplayCopyDisplayMode(d), m.width > 0 { escala = Double(m.pixelWidth) / Double(m.width) }
  let uuid = CGDisplayCreateUUIDFromDisplayID(d).map { CFUUIDCreateString(nil, $0.takeRetainedValue())! as String } ?? ""
  print("DISPLAY|\(uuid)|\(Int(b.minX)),\(Int(b.minY)),\(Int(b.width)),\(Int(b.height))|\(escala)|main=\(CGDisplayIsMain(d) != 0)")
}
let wins = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] ?? []
for w in wins {
  let owner = w[kCGWindowOwnerName as String] as? String ?? ""
  guard owner == "zoom.us" || owner == "Zoom" || owner == "Zoom Workplace" else { continue }
  let b = w[kCGWindowBounds as String] as? [String: Any] ?? [:]
  let x = b["X"] as? Double ?? 0, y = b["Y"] as? Double ?? 0
  let wd = b["Width"] as? Double ?? 0, h = b["Height"] as? Double ?? 0
  if wd < 300 || h < 200 { continue }
  print("WINDOW|\(w[kCGWindowNumber as String] ?? 0)|\(w[kCGWindowName as String] as? String ?? "")|\(Int(x)),\(Int(y)),\(Int(wd)),\(Int(h))|\(w[kCGWindowLayer as String] ?? 0)")
}
