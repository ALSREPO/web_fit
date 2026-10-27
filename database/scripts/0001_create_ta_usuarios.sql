CREATE TABLE IF NOT EXISTS `ta_usuarios` (
  `idusuario` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `password` varchar(200) NOT NULL,
  `fechaCreacion` date NOT NULL,
  `email` varchar(60) NOT NULL DEFAULT 'na@na.com',
  `activo` tinyint NOT NULL DEFAULT '0', -- 0: usuario sin activar el mail, 10: usuario con registro completo, >=20: usuario administrador
  `email_verificado` BOOLEAN NOT NULL DEFAULT FALSE, -- campo para verificar el email
  PRIMARY KEY (`idusuario`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
