import models.Models
import db.db_manager

da = db.db_manager.db_address_manager()
dc = db.db_manager.db_client_manager()
add1 = models.Models.Address("New York")
add2 = models.Models.Address("Paseo Rojas")
add3 = models.Models.Address("Nose que")
cc = models.Models.Client("nombre", "apellidos", "nuevodni")
dc.insert_client(cc)
cc.address.append(add1)
dc.session.add(cc)

self.assertFalse(da.address_exist(add1))
self.assertFalse(da.address_exist(add2))

dc.insert_address(add2)
dc.insert_address(add3)

self.assertTrue(add2.clients == cc)
self.assertTrue(add1.clients == cc)
self.assertTrue(isinstance(cc.address.index(add2), int))
self.assertTrue(da.address_exist(add1))
self.assertTrue(da.address_exist(add2))
