def generarPedido(cliente){

  var listaProductosEnPedido = componente
  var subtotal, total, factura
  
  factura["nombreCliente"] = obtenerNombreCliente(cliente)
  factura["codigoCliente"] = obtenerCodigoCliente(cliente)
  var detalleFactura[]
  for producto in listaProductosEnPedido
    var filaEnFactura[]
    filaEnFactura["nombreProducto"] = obtenerNombreProducto(producto)
    if(verificarExistencia(producto))
      sutotal += obtenerPrecio(producto) * cantidadSolicitada(producto)
      filaEnFactura["precioProducto"] = obtenerPrecio(producto)
      filaEnFactura["cantidadSolicitadaProducto"] = cantidadSolicitada(producto)
    total += subtotal
    detalleFactura[] = filaEnFactura
  factura["detalleFactura"] = detalleFactura
  factura["montoTotal"] = total
  
  if(clientePagaEfectivo){
    vuelto = total-obtenerDinero(cliente)
    entregarVuelto(vuelto)
  }
  else{
    realizarCobroTarjetaDeCredito(obtenerNumeroTarjetaCredito(cliente),obtenerCVVTarjetaCredito)
    notificarCobro()
  }
}


