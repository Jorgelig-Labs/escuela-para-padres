// ocr <imagen.png>: texto reconocido con su caja en píxeles (origen arriba a la izquierda).
// Salida: texto|x|y|ancho|alto
import Foundation
import Vision
import AppKit

let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let img = NSImage(contentsOf: url),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let W = Double(cg.width), H = Double(cg.height)
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.recognitionLanguages = ["es-MX", "en-US"]
try VNImageRequestHandler(cgImage: cg).perform([req])
for obs in req.results ?? [] {
  guard let t = obs.topCandidates(1).first else { continue }
  let b = obs.boundingBox
  print("\(t.string)|\(Int(b.minX * W))|\(Int((1 - b.maxY) * H))|\(Int(b.width * W))|\(Int(b.height * H))")
}
