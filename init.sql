-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: localhost    Database: interview2
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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add lda',7,'add_lda'),(26,'Can change lda',7,'change_lda'),(27,'Can delete lda',7,'delete_lda'),(28,'Can view lda',7,'view_lda'),(29,'Can add faq',8,'add_faq'),(30,'Can change faq',8,'change_faq'),(31,'Can delete faq',8,'delete_faq'),(32,'Can view faq',8,'view_faq'),(33,'Can add interview',9,'add_interview'),(34,'Can change interview',9,'change_interview'),(35,'Can delete interview',9,'delete_interview'),(36,'Can view interview',9,'view_interview'),(37,'Can add question',10,'add_question'),(38,'Can change question',10,'change_question'),(39,'Can delete question',10,'delete_question'),(40,'Can view question',10,'view_question'),(41,'Can add bertopic',11,'add_bertopic'),(42,'Can change bertopic',11,'change_bertopic'),(43,'Can delete bertopic',11,'delete_bertopic'),(44,'Can view bertopic',11,'view_bertopic');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (24,'pbkdf2_sha256$870000$9fidUhmiDJaWyMKzjlyATD$rWvAJYHQ45i3gfb5xYrd1IwqAWVfa79apRoCBXHJcL8=','2025-08-19 23:52:08.379215',1,'adminuser','','','',1,1,'2022-11-08 11:23:04.566835');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `count` int DEFAULT NULL,
  `chat_id` int DEFAULT NULL,
  `summary_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CHAT_ID` (`chat_id`),
  KEY `SUMMARY_ID` (`summary_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1475 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `session_id` varchar(256) DEFAULT NULL,
  `question` text,
  `response` text,
  `timestamp` datetime DEFAULT NULL,
  `time` int DEFAULT NULL,
  `word_count` int DEFAULT NULL,
  `topic` int DEFAULT NULL,
  `int_id` int DEFAULT NULL,
  `interview_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5587 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat`
--

LOCK TABLES `chat` WRITE;
/*!40000 ALTER TABLE `chat` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(11,'management','bertopic'),(8,'management','faq'),(9,'management','interview'),(7,'management','lda'),(10,'management','question'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2020-04-10 22:01:30.191119'),(2,'auth','0001_initial','2020-04-10 22:01:30.577001'),(3,'admin','0001_initial','2020-04-10 22:01:31.936424'),(4,'admin','0002_logentry_remove_auto_add','2020-04-10 22:01:32.250035'),(5,'admin','0003_logentry_add_action_flag_choices','2020-04-10 22:01:32.257660'),(6,'contenttypes','0002_remove_content_type_name','2020-04-10 22:01:32.483415'),(7,'auth','0002_alter_permission_name_max_length','2020-04-10 22:01:32.508099'),(8,'auth','0003_alter_user_email_max_length','2020-04-10 22:01:32.532743'),(9,'auth','0004_alter_user_username_opts','2020-04-10 22:01:32.545209'),(10,'auth','0005_alter_user_last_login_null','2020-04-10 22:01:32.655105'),(11,'auth','0006_require_contenttypes_0002','2020-04-10 22:01:32.663338'),(12,'auth','0007_alter_validators_add_error_messages','2020-04-10 22:01:32.676280'),(13,'auth','0008_alter_user_username_max_length','2020-04-10 22:01:32.696770'),(14,'auth','0009_alter_user_last_name_max_length','2020-04-10 22:01:32.720979'),(15,'auth','0010_alter_group_name_max_length','2020-04-10 22:01:32.745658'),(16,'auth','0011_update_proxy_permissions','2020-04-10 22:01:32.758521'),(17,'sessions','0001_initial','2020-04-10 22:01:32.819623'),(18,'management','0001_initial','2022-11-30 19:13:14.382257'),(19,'management','0002_lda_numtopics','2022-11-30 19:13:14.405872'),(20,'management','0003_alter_lda_duration_alter_lda_endingdate_and_more','2022-11-30 19:13:14.660728'),(21,'management','0004_lda_coherence','2022-12-06 10:38:36.382074'),(22,'management','0005_lda_error','2022-12-06 10:38:36.484687'),(23,'management','0006_alter_lda_error','2022-12-06 10:38:36.594997'),(24,'management','0007_faq','2022-12-11 16:33:38.749367'),(25,'management','0008_interview_question','2023-01-02 17:16:19.814824'),(26,'management','0009_rename_interview_id_question_interview','2023-01-02 17:16:20.136395'),(27,'management','0010_interview_note','2023-01-02 17:16:20.164971'),(28,'management','0011_interview_respect_order','2023-01-02 17:16:20.199058'),(29,'management','0012_remove_question_created_at_and_more','2023-01-02 17:16:20.269402'),(30,'management','0013_question_created_at_question_updated_at','2023-01-02 17:16:20.329249'),(31,'management','0014_rename_order_question_question_order','2023-01-02 17:16:20.353653'),(32,'management','0015_question_conclusion','2023-05-02 07:13:22.023936'),(33,'management','0016_lda_htmloutputfile','2023-05-02 07:13:22.054054'),(34,'management','0017_bertopic','2023-05-18 14:15:58.052600');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `session_id` varchar(256) DEFAULT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `clarity` text,
  `summary` text,
  `features` text,
  `other` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=291 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interactions`
--

DROP TABLE IF EXISTS `interactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `started` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interactions`
--

LOCK TABLES `interactions` WRITE;
/*!40000 ALTER TABLE `interactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `interactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_bertopic`
--

DROP TABLE IF EXISTS `management_bertopic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_bertopic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startingDate` datetime(6) NOT NULL,
  `endingDate` datetime(6) DEFAULT NULL,
  `duration` decimal(10,3) DEFAULT NULL,
  `numTopics` decimal(10,3) NOT NULL,
  `status` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `corpusFile` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `outputFile` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `HTMLoutputFile` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `topic` int NOT NULL,
  `coherence` decimal(10,3) DEFAULT NULL,
  `error` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_bertopic`
--

LOCK TABLES `management_bertopic` WRITE;
/*!40000 ALTER TABLE `management_bertopic` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_bertopic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_faq`
--

DROP TABLE IF EXISTS `management_faq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_faq` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic` int NOT NULL,
  `question` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `answer` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_faq`
--

LOCK TABLES `management_faq` WRITE;
/*!40000 ALTER TABLE `management_faq` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_faq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_interview`
--

DROP TABLE IF EXISTS `management_interview`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_interview` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic_id` int NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `note` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `respect_order` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `management_lda`
--

DROP TABLE IF EXISTS `management_lda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_lda` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startingDate` datetime(6) NOT NULL,
  `endingDate` datetime(6) DEFAULT NULL,
  `duration` decimal(10,3) DEFAULT NULL,
  `status` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `corpusFile` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `outputFile` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `topic` int NOT NULL,
  `numTopics` decimal(10,3) NOT NULL,
  `coherence` decimal(10,3) DEFAULT NULL,
  `error` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `HTMLoutputFile` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_lda`
--

LOCK TABLES `management_lda` WRITE;
/*!40000 ALTER TABLE `management_lda` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_lda` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_lexicon`
--

DROP TABLE IF EXISTS `management_lexicon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_lexicon` (
  `id` int NOT NULL AUTO_INCREMENT,
  `word` varchar(128) DEFAULT NULL,
  `category` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNI_COMBO` (`category`,`word`)
) ENGINE=InnoDB AUTO_INCREMENT=10621 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_lexicon`
--

LOCK TABLES `management_lexicon` WRITE;
/*!40000 ALTER TABLE `management_lexicon` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_lexicon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_lexicon_topic`
--

DROP TABLE IF EXISTS `management_lexicon_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_lexicon_topic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(128) DEFAULT NULL,
  `topic` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_lexicon_topic`
--

LOCK TABLES `management_lexicon_topic` WRITE;
/*!40000 ALTER TABLE `management_lexicon_topic` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_lexicon_topic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_question`
--

DROP TABLE IF EXISTS `management_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_question` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `topic_id` int NOT NULL,
  `question_order` int NOT NULL,
  `interview_id` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `conclusion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `management_question_interview_id_1f8cda86_fk_managemen` (`interview_id`),
  CONSTRAINT `management_question_interview_id_1f8cda86_fk_managemen` FOREIGN KEY (`interview_id`) REFERENCES `management_interview` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_question`
--

LOCK TABLES `management_question` WRITE;
/*!40000 ALTER TABLE `management_question` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_reflection`
--

DROP TABLE IF EXISTS `management_reflection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_reflection` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reflection` longtext NOT NULL,
  `conditions` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `interview_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `management_reflectio_interview_id_ec6de019_fk_managemen` (`interview_id`),
  CONSTRAINT `management_reflectio_interview_id_ec6de019_fk_managemen` FOREIGN KEY (`interview_id`) REFERENCES `management_interview` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_reflection`
--

LOCK TABLES `management_reflection` WRITE;
/*!40000 ALTER TABLE `management_reflection` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_reflection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_survey`
--

DROP TABLE IF EXISTS `management_survey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_survey` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(45) DEFAULT NULL,
  `text` varchar(256) DEFAULT NULL,
  `topic` int DEFAULT NULL,
  `intro` int DEFAULT NULL,
  `outro` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_survey`
--

LOCK TABLES `management_survey` WRITE;
/*!40000 ALTER TABLE `management_survey` DISABLE KEYS */;
/*!40000 ALTER TABLE `management_survey` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `management_topics`
--

DROP TABLE IF EXISTS `management_topics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `management_topics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic` varchar(128) DEFAULT NULL,
  `cpname` varchar(45) DEFAULT NULL,
  `iconfile` varchar(128) DEFAULT NULL,
  `intro_disclaimer` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `management_topics`
--

LOCK TABLES `management_topics` WRITE;
/*!40000 ALTER TABLE `management_topics` DISABLE KEYS */;
INSERT INTO `management_topics` VALUES (1,'bioethics','C.P.','1.png','We are studying people’s opinions about current organoids research.\n\nIn this study, you will be interviewed about your thoughts and opinions surrounding organoids research. For this interview, you will be interacting with a computer-based interview tool we have developed. Please note that the system is not designed to respond in human-like ways, but rather to facilitate the collection of your valuable feedback. The system may not always respond appropriately, but please try to respond in a way that provides the information requested. This research project is being conducted by researchers in bioethics, computer science, and other disciplines.\n\nEverything you write will be kept completely confidential. In fact, since the interview is conducted by a computer program, you should feel free to be even more honest and direct than you might usually be. Note that this is meant to be a personal interview to learn more about your personal thoughts and experiences. Hopefully, by answering these questions, you will learn more about your own reactions to this emerging technology. Note that the interview might be used for other research purposes.\n\nYour participation may ultimately help us to come up with better interviewing methods and help us to better understand public opinion about emerging technologies. By clicking on the Submit button below, you agree to participate in our study. Please take our project seriously and thank you so much for your help.\n\nIf you are ready to go, click the \'Submit\' button below. '),(14,'organoids','C.P.','14.png',NULL),(15,'halloween','Boo','15.jpg',NULL),(16,'substance_abuse','Bot','16.png','test update3'),(17,'personality','C.P','17.png',NULL),(18,'mental_health','C.P.','18.png',NULL),(19,'covid19','C.P.','19.png','We are learning how the Coronavirus outbreak is affecting people. We would like your perspective on how the outbreak has touched different parts of your life.\n\nIn this study, you will be interviewed about your experiences, thoughts, and feelings about the COVID outbreak. For this interview, you will be interacting with a computer-based interview tool we have developed. This research project is being conducted by researchers in psychology, computer science, and other disciplines.\n\nEverything you write will be kept completely confidential. In fact, since the interview is conducted by a computer program, you should feel free to be even more honest and direct than you might usually be. Note that this is meant to be a personal interview to learn more about your reactions to the pandemic. Hopefully, by answering these questions, you will learn more about your own reactions to the outbreak.\n\nYour participation may ultimately help us to come up with better interviewing methods that can help people in distress. By clicking on the Submit button below, you agree to participate in our study. Please take our project seriously and thank you so much for your help.\n\nNote: if you are participating in the Prolific study, you must spend at least 15 minutes in this writing task. If you do not spend at least 15 minutes on this task, we will reject your work without payment. Try to write at least 3 sentences per response to increase the time spent writing.\n\nIf you are ready to go, click the \'Submit\' button below.'),(20,'long_covid','C.P.','20.png',NULL),(21,'test_project','C.P.','21.png','We are studying people’s opinions about current organoids research.\r\n\r\nIn this study, you will be interviewed about your thoughts and opinions surrounding organoids research. For this interview, you will be interacting with a computer-based interview tool we have developed. Please note that the system is not designed to respond in human-like ways, but rather to facilitate the collection of your valuable feedback. The system may not always respond appropriately, but please try to respond in a way that provides the information requested. This research project is being conducted by researchers in bioethics, computer science, and other disciplines.\r\n\r\nEverything you write will be kept completely confidential. In fact, since the interview is conducted by a computer program, you should feel free to be even more honest and direct than you might usually be. Note that this is meant to be a personal interview to learn more about your personal thoughts and experiences. Hopefully, by answering these questions, you will learn more about your own reactions to this emerging technology. Note that the interview might be used for other research purposes.\r\n\r\nYour participation may ultimately help us to come up with better interviewing methods and help us to better understand public opinion about emerging technologies. By clicking on the Submit button below, you agree to participate in our study. Please take our project seriously and thank you so much for your help.\r\n\r\nIf you are ready to go, click the \'Submit\' button below. ');
/*!40000 ALTER TABLE `management_topics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `summary`
--

DROP TABLE IF EXISTS `summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `summary` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `session_id` varchar(256) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `time` int DEFAULT NULL,
  `word_count` int DEFAULT NULL,
  `topic` int DEFAULT NULL,
  `int_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=494 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `summary`
--

LOCK TABLES `summary` WRITE;
/*!40000 ALTER TABLE `summary` DISABLE KEYS */;
/*!40000 ALTER TABLE `summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `survey`
--

DROP TABLE IF EXISTS `survey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `survey` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(256) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `before_writing` tinyint DEFAULT NULL,
  `topic_id` int DEFAULT NULL,
  `question_id` int DEFAULT NULL,
  `answer` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1651 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_extra`
--

DROP TABLE IF EXISTS `user_extra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_extra` (
  `id` int NOT NULL AUTO_INCREMENT,
  `display_name` varchar(64) DEFAULT NULL,
  `user_id` varchar(256) NOT NULL,
  `session_id` varchar(128) DEFAULT NULL,
  `study_id` varchar(128) DEFAULT NULL,
  `prolific_id` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=614 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_extra`
--

LOCK TABLES `user_extra` WRITE;
/*!40000 ALTER TABLE `user_extra` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_extra` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-15 23:28:39
