**X = Oui,  O = Non**

|                    |Visiteur	|Élève 	|Professeur |Admin |
|--------------------|:--------:|:-----:|:---------:|:----:|
|**Comptes utilisateurs**|||||				
|Ajout d’un compte professeur ou admin|	O|	O|	O|	X|
|Ajout d’un compte élève|	O|	O|	O?|	X|
|Modification d’un compte utilisateur autre que le sien|	O|	O|	X|	X|
|**Métadonnées**|||||				
|Ajout d’un document / initialisation d’un dossier|	O|	O|	X|	X|
|Modification des métadonnées|	O|	O|	X|	X|
|Lecture des métadonnées|	X|	X|	X|	X|
|**Transcription**|||||				
|Lecture de la transcription de l’élève A (+ les notes associées)|	O|	X pour l’élève A, O sinon|	X|	X|
|Modification de la transcription de l’élève A (+ les notes associées)|	O|	X pour l’élève A, O sinon|	O|	X|
|Lecture de la transcription du professeur|	X| 	X| 	X|	X|
|Modification de la transcription du professeur (+ les notes associées)|	O|	O|	X|	X|
|Copie de la transcription d’un élève vers son propre compte + les notes associées|	O|	O|	X|	X|
|**Traduction**|||||				
|Lecture de la traduction de l’élève A|	O|	X pour l’élève A, O sinon|	X|	X|
|Modification de la traduction de l’élève A|	O|	X pour l’élève A, O sinon|	O| 	X|
|Lecture de la traduction du professeur|	X|	X|	X|	X|
|modification de la traduction du professeur|	O|	O|	X|	X|
|Copie de la traduction d’un élève vers son propre compte|	O|	O|	X|	X|
|Alignement de la traduction|	O|	O|	X|	X|
|**Facsimile**|||||				
|Découpage du facsimile en zones| 	O|	X|	X|	X|
|Alignement d’une zone avec la transcription de référence|	O|	X|	X|	X|
|Annotation de zones du facsimile|	O|	X|	X|	X|
|Visualisation du découpage d’un élève A et lecture de l’alignement et des notes associées|	O|	X pour l’élève A, O sinon|	X|	X|
|Visualisation du découpage du professeur et lecture de l’alignement et des notes associées|	X|	X|	X|	X|
|Copie du découpage en zone d’un élève (+ alignement + notes associées)|	O|	O|	X|	X|
|**Commentaires**|||||				
|Lecture des commentaires du professeur (+ les notes associées)| 	X|	X|	X|	X|
|Modifications des commentaires du professeur (+ les notes associées)|	O|	O|	X|	X|
|Lecture des commentaires de l’élève A (+ les notes associées)|	O|	X pour l’élève A, O sinon|	X|	X|
|Modification des commentaires de l’élève A (+ les notes associées)|	O|	X pour l’élève A, O sinon|	X|	X|
|Copie d’un commentaire d’un élève vers son propre compte (+ les notes associées)|	O|	O|	X|	X|
|**Parties du discours**|||||				
|Lecture des parties de discours du professeur (+ les notes associées)|	X|	X|	X|	X|
|Modifications des parties de discours  du professeur (+ les notes associées)|	O|	O|	X|	X|
|Lecture des parties de discours de l’élève A (+ les notes associées)|	O|	X pour l’élève A, O sinon|	X|	X|
|Modification des parties de discours de l’élève A (+ les notes associées)|	O|	X pour l’élève A, O sinon|	X|	X|
|Copie de la segmentation en partie de discours d’un élève (+ les notes associées)|	O|	O|	X|	X|

Les fonctionnalités « **copie** » signifient, pour un professeur ou un admin : remplacer son propre contenu (s’il existe) par le contenu de la page en cours via le clique sur un bouton. C’est en quelque sortes un import de données pour que le professeur ne travaille pas *ex nihilo* mais à partir des données d’un élève.
