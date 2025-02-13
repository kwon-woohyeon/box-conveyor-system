-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: logistics
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(45) NOT NULL,
  `phone` varchar(45) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT '0',
  `created_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_date` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'aaa111','scrypt:32768:8:1$uqOgFhaoBjImTy4X$27d1b7f16d7d5916713cfd40619a08619e726c002acc15fb6afe1948d102a1fc6a4733eb5ad60e2feccf6650ba556fc9ba087b34eb1354085212f28693144fe5','이진혁1','01012341331',1,'2024-11-08 14:52:52','2024-11-15 11:48:26'),(4,'bbb','scrypt:32768:8:1$Mgbv2OsKv8YyPmaw$23db84ac89072241a39083b6544226b5212fbbee43061f3d22a40836b438ef93af8f22dc30712b2a5534e4afe80dfa4d11de2a72b9fcbcdd037f086e2d6b4325','권우현','01044445555',1,'2024-11-11 18:37:14','2024-11-14 15:35:54'),(5,'ccc','scrypt:32768:8:1$yiuKtTrJV1J2iHSn$f90ef281fcb139646df670fbfee01a5a34a6c0d2d189da58bfcf36eae39304a4b756aa32807efe444072a64d91181f4dfb42de89d794b7720a08376b61429fd3','윤주원','01066668888',1,'2024-11-11 18:39:51','2024-11-14 15:36:22'),(7,'www','scrypt:32768:8:1$Hk32zkQNRoCAlTt0$c6a17e0fe00236e5c7d3e9ab37716519045de60ee75a1f45ceaa34540659d0104c4669e6615b67940c66fa777c4686e841889ea5548f8d3cc710045be8b2cb53','송민영','01055557777',0,'2024-11-11 18:45:50','2024-11-14 15:35:54'),(8,'eee','scrypt:32768:8:1$nXcykEzrGHYOqdZ9$5497881053e6d33008c6ac0a4826bbd3e42d5ed066d35cfc9b682eb0f06740060bc35aa02f40b763e81fbbec04f37fd367932418d07f045786ea657c64ba0a44','권우현','01065654545',0,'2024-11-11 18:47:41','2024-11-14 15:35:54'),(10,'a','scrypt:32768:8:1$2VCiIDR5R5REvMEP$acb4730061c419e6d43a3d85f4713d8f3c77f48a3978cfbb43d6aee1083dfa73b53bdced8ec07b70429b2371bf7072468f53475703e229d01beb0dcebc9fc572','박진형','01055556688',0,'2024-11-12 20:39:46','2024-11-14 15:35:54'),(11,'rnjsdngus','scrypt:32768:8:1$1zC0iX8m2gk5dnGE$628823f7756724c43c0c45cf6609e4b30fc3c99ab699243c63efced7886d307d313b62352f55e42991c93c797a8acaff216ad9777565468ed998a76af2d2a0e9','권우현','01012347895',0,'2024-11-15 10:46:17',NULL),(13,'dlwlsgur123','scrypt:32768:8:1$vc2eTgkMmQsu7yHq$5c695c1dea9cad4f7f86bec1a5bc9a4a794d0d9fa42e2a73845ebb744ca2b5ddbe423041304ab6fb9a2c1fca748ef217ae84813529536cdfcb8ecd1725a14ac4','이진혁123','0105788411',0,'2024-11-15 11:51:10',NULL),(14,'dlwlsgur123','scrypt:32768:8:1$oZw1rmaoWRNoWczR$2dbdd12b8ae75c3bb4bf650f8046056b51adf0dab252ecbd323257475ba436a37dc5926b6ff43824d8c1f9248e7da21d46c7537f3a23ac35bd87a07f19793c0f','허주옥1','0105777884',1,'2024-11-15 11:51:58','2024-11-15 11:52:17');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-15 18:21:21
