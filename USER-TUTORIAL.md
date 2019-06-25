Adele, tutoriel
===

## Synthèse

Adele est une application pédagogique de saisie collaborative de documents diplomatiques.  
Un professeur crée un nouveau document et l’attribue à une liste d’élèves.

Le scénario de travail avec les élèves est le suivant :
* Gestion du nouveau document
  1. `teacher` [Le professeur crée un nouveau document.](#create_doc)
  1. `teacher` [Le professeur saisit la notice du nouveau document.](#update_meta)
  1. `teacher` [Le professeur assigne le nouveau document à une liste d’utilisateurs (groupe d’élèves).](#assignation_doc)

* Transcription
  1. `student` [Les élèves transcrivent le document.](#transcription)
  1. `teacher` [Le professeur consulte les transcriptions des élèves.](#view_student_transcription)
  1. `teacher` Le professeur transcrit OU [clone la transcription de son choix et la corrige](#clone_transcription).
  1. `teacher` Le professeur publie sa transcription de référence.
  1. `teacher` [Le professeur lie la transcription à l’image.](#facsim)

* Traduction (optionnelle)
  1. `student` [Les élèves traduisent la transcription de référence.](#traduction)
  1. `teacher` Le professeur consulte les traductions des élèves.
  1. `teacher` Le professeur traduit OU clone la traduction de son choix et la corrige.
  1. `teacher` Le professeur met à disposition des élèves sa traduction de référence.

* Parties du discours
  1. `student` [Les élèves identifient et commentent les parties du discours sur la transcription de référence.](#speech)
  1. `teacher` Le professeur consulte l’identification des parties des discours des élèves.
  1. `teacher` Le professeur identifie les parties du discours ou clone l’identification de son choix et la corrige. / et la publie ?
  1. [`teacher` Le professeur publie son identification des parties du discours ?]

* Commentaires
  1. `student` [Les élèves rédigent des commentaires libres.](#comment_edit)
  1. `teacher` Le professeur consulte les commentaires des élèves.
  1. `teacher` Le professeur rédige ses commentaires ET/OU clone des commentaires des élèves et les corrige.
  1. `teacher` Le professeur publie les commentaires de référence.

* Facsimilé
  1. `user ?` [Un utilisateur aligne la transcription à l’image.](#facsim)

Un chercheur peut aussi utiliser l’application seul pour éditer et commenter des documents diplomatiques.


## Gestion des utilisateurs et des listes d’utilisateurs

### Rôles, définitions

On distingue différents types d’utilisateurs (rôles) :

|rôle|définition|droits|
|----|----------|------|
|`visitor`|utilisateur non identifié|<ul><li>consulter les documents publiés</li></ul>|
|`student`|élève|<ul><li>*idem* `visitor`</li><li>gérer son profil</li><li>consulter les documents non publiés</li><li>éditer les documents attribués</li></ul>|
|`teacher`|professeur|<ul><li>*idem* `student`</li><li>créer/supprimer un document</li><li>gérer les élèves</li><li>gérer les listes d’utilisateurs</li><li>consulter les travaux (transcription, traduction, etc.) des élèves</li><li>soumettre les contenus de référence (transcription, etc.)</li><li>publier/dépublier un document</li></ul>|
|`admin`|administrateur|<ul><li>*idem* `teacher`</li><li>gérer les professeurs</li></ul>|


### Gérer son profil

> `@role: admin, teacher, student`, menu [`Tableau de bord > Mon profil`](https://dev.chartes.psl.eu/adele/user/edit_user_profile)  
https://dev.chartes.psl.eu/adele/user/edit_user_profile

Un utilisateur peut :
* modifier son prénom, son nom et son pseudo ;
* mettre à jour son mot de passe.

**TODO :** reprendre (unifier) le formulaire.


### Gérer les élèves et les listes d’utilisateurs

> `@role: admin, teacher`, menu [`Utilisateurs`](https://dev.chartes.psl.eu/adele/dashboard/manage-users)  
https://dev.chartes.psl.eu/adele/dashboard/manage-users

**`admin` et `teacher` peuvent :**
* inviter un nouvel élève (`student`) ;
* désactiver le compte d’un élève ;
* créer une nouvelle liste d’utilisateur(s) (par ex. une liste par classe ou groupe de travail) ;
* assigner un utilisateur à une ou plusieurs liste(s) ;
* révoquer un utilisateur d’une liste ;
* supprimer une liste d’utilisateur(s).

#### Un professeur invite un nouvel élève.
* Saisir l’adresse mail de l’élève et cliquer sur `Inviter un utilisateur`.
* L’utilisateur reçoit un mail d’invitation et suit la procédure d’inscription.
* **NB** :  l’utilisateur invité se voit nécessairement attribué le rôle `student`.
* **TODO** : implémenter l’envoi du mail et la procédure d’inscription.

#### Un professeur désactive le compte d’un/de plusieurs élève(s).
* Sélectionner un ou plusieurs élèves.
* Cliquer sur le bouton `Désactiver le compte de l’utilisateur`.
* **TODO** : implémenter la désactivation de compte(s).
* **TODO** : pouvoir lister tous les utilisateurs – en l’état on liste les seuls utilisateurs non assignés à la `Liste` sélectionnée (à droite).
* **Revoir : en l’état, tous les utilisateurs sont listés, or un professeur ne peut désactiver que le compte des élèves (et non des professeurs et admin…)**

#### <a name="user_lists"></a>Un professeur crée une nouvelle liste d’utilisateur(s).
* Saisir un nouveau nom de liste **explicite** (par ex. `AP1-2018`) puis clique sur `Créer une liste`.
* **TODO** : interdire la création d’une liste intitulée comme une liste déjà existante.

#### Un professeur assigne un/des utilisateur(s) à une liste.
* Sélectionner une liste dans le menu déroulant `Listes existantes`.
* Sélectionner un ou plusieurs utilisateurs(s) dans la liste des utilisateurs (colonne de gauche).
* Cliquer sur la flèche `->` pour ajouter le(s) utilisateur(s) sélectionné(s) à la liste.

#### Un professeur révoque un/des utilisateurs d’une liste.
* Sélectionner une liste dans le menu déroulant `Listes existantes`.
* Sélectionner un ou plusieurs utilisateur(s) de la liste (colonne de droite).
* Cliquer sur la flèche `<-` pour retirer le(s) utilisateur(s) sélectionné(s) de la liste.

#### Un professeur supprime une liste d’utilisateur(s).
* Sélectionner une liste dans le menu déroulant `Listes existantes`.
* Cliquer sur le bouton `Supprimer la liste`.


### Gérer les professeurs

> `@role: admin`, menu `???`

* Un administrateur invite un nouveau professeur.
* Un administrateur désactive le compte d’un professeur.

**TODO** : implémenter les fonctionnalités.


## Gestion des documents

### <a name="create_doc"></a>Création d’un document

> `@role: teacher`, menu [`Mes documents`](https://dev.chartes.psl.eu/adele/dashboard/documents)  
https://dev.chartes.psl.eu/adele/dashboard/documents

Seul un professeur peut créer un nouveau document.  
Par défaut, un nouveau document ne contient qu’un titre et un sous-titre descriptif.

**Un professeur crée un nouveau document.**
* En bas de la page, dans la fenêtre `Ajouter un nouveau document`, saisir le titre et le Sous-titre ;
* cliquer sur `Ajouter le documents`.

**Un professeur associe des images au nouveau document.**
* Cliquer sur `Lier un manifeste` ;
* Rédiger tuto

**Un professeur met à jour les images associées à un document.**
* Rédiger tuto


### Suppression d’un document

> `@role: teacher`, menu [`Mes documents`](https://dev.chartes.psl.eu/adele/dashboard/documents)  
https://dev.chartes.psl.eu/adele/dashboard/documents

**Un professeur supprime un document.**
* Dans la ligne du *dashbord* décrivant le document, cliquer sur le bouton `Supprimer` ;
* dans le menu contextuel qui apparaît, cliquer sur le bouton `Confirmer la suppression`.


### <a name="assignation_doc"></a>Attribution d’un document

> `@role: teacher`, menu [`Utilisateurs`](https://dev.chartes.psl.eu/adele/dashboard/manage-users)  
https://dev.chartes.psl.eu/adele/dashboard/manage-users

Un document n’est pas associé directement à un/des utilisateur(s) mais à une [liste prédéfinie d’utilisateurs](#user_lists).
Une liste peut représenter :
* une classe : tous les élèves d’une classe ;
* un groupe de travail : un groupe de contributeurs constitué pour l’édition d’une série particulière ;
* un élève seul.

Par défaut, un nouveau document n’est associé à aucune liste.

#### Un professeur assigne un document à une liste d’utilisateur(s).
* Dans le tableau des documents, sélectionner dans le menu déroulant la liste d’utilisateurs voulue.

#### Un professeur délie un document de toute liste d’utilisateur(s).
* Dans le tableau des documents, sélectionner dans le menu déroulant `Aucune liste`.

**Question** : un professeur invité sur une liste a-t-il les mêmes droits que les élèves de la liste ou a-t-il les droits étendu du professeur qui a soumis le document ?  
**TODO** : s’assurer que seuls le professeur propriétaire pour éditer la transcription de référence  
**TODO** : sortir la gestion de l’attribution de la page de gestion des utilisateurs, pour https://dev.chartes.psl.eu/adele/dashboard/documents


## Édition d’un document

> `@role: admin, teacher, student`, menu `Éditer`  
https://dev.chartes.psl.eu/adele/documents/&lt;doc_id>/edition

Seuls les utilisateurs appartenant à la liste associée au document peuvent éditer ce document.  

**Définitions** :
* **Notice** : les métadonnées structurées du document.
* **Transcription** : la transcription enrichie (typographie et annotations) du document.
* **Traduction** : la traduction ***optionnelle*** de la transcription.
* **Facsimilé** : alignements **optionnels** de la transcription et des zones de l’image.
* **Parties du discours** : segmentation ***optionnelle*** de la transcription en parties du discours (typologie de la [CID](http://www.cei.lmu.de/index.php)).
* **Commentaires** : commentaires ***optionnels*** libres enrichis (typographie et annotations) de différents types (historique, juridique, paléographique, philologique, sigillographique).

Un élève inscrit dans la liste d’utilisateurs associé à un document peut l’éditer :
* dans le délai défini par le professeur ;
* tant que le professeur n’a pas soumis sa transcription de référence.


### <a name="update_meta"></a>Saisie des métadonnées
`@role: teacher`

* `update`: seul le professeur qui a créé le document peut mettre à jour la notice.

**Question** : permettre l’inscription de plusieurs éditeurs ?


### <a name="transcription"></a>Transcription
`@role: student, teacher`

#### Scénario
* Un élève lié au document saisit une transcription, avant la date limite fixée par le professeur.
* Le professeur peut consulter la transcription de chaque élève, mais **pas l’éditer (?)**.
* Le professeur soumet une **transcription de référence** :
  * soit en la saisissant ;
  * soit en s’attribuant la transcription d’un élève pour la corriger.
* Un élève ne peut plus transcrire dès que la date limite est passée.
* Un élève ne peut plus transcrire dès que la transcription de référence est soumise.
* La transcription de référence n’est pas éditable par un élève.


#### Le professeur fixe la date limite d’édition d’un document.
* Dans le menu [`Tableau de bord > Mes documents`](https://dev.chartes.psl.eu/adele/dashboard/documents), dans la colonne `Date limite de modification`, cliquer sur la date et sélectionner la date souhaitée.
* **TODO** : expliciter cette date… minuit ?


#### <a name="view_student_transcription"></a>Le professeur consulte la transcription d’un élève.
* Dans la fenêtre d’édition du document (https://dev.chartes.psl.eu/adele/documents/&lt;doc_id>/edition), cliquer sur l’étiquette correspondant à l’utilisateur courant, à droite de la référence du document ;
* dans le menu contextuel `Auteur des travaux à afficher`, sélectionner l’élève dont on souhaite consulter le travail et cliquer sur `Valider`.
* NB : l’étiquette de l’utilisateur indique l’auteur de la transcription consultée.
* NB : cliquer à nouveau sur cette étiquette pour sélectionner la transcription d’un nouvel élève ou revenir à sa propre transcription.

#### <a name="clone_transcription"></a>Le professeur clone la transcription d’un elève.
* **TODO** : implémenter la fonctionnalité.


#### TODO
* Gestion des sauts de paragraphe : en lecture et en édition
* `teacher` : tester la visualisation des contenus des élèves (s’assurer qu’aucun contenu ne soit perdu en base à la bascule)
* `teacher` : finaliser le clonage du contenu `student` avec l’ensemble des annotations associées.
* `teacher` : prévoir une case pour publier une transcription de référence
* `teacher` : suppression de sa transcription


### <a name="traduction"></a>Traduction
`@role: student, teacher`


#### Scénario
* La traduction **n’est pas éditable**, tant que le professeur n’a pas soumis de transcription de référence.
* Un élève lié au document saisit une traduction en regard de la transcription de référence (non éditable), avant la date limite fixée par le professeur.
* Le professeur peut consulter la traduction de chaque élève, mais **pas l’éditer (?)**.
* Le professeur soumet une **traduction de référence** :
  * soit en la saisissant ;
  * soit en s’attribuant la traduction d’un élève pour la corriger.
* Un élève ne peut plus traduire dès que la date limite est passée.
* Un élève ne peut plus traduire dès que la traduction de référence est soumise.
* La traduction de référence n’est pas éditable par un élève.


**Bugs / questions :**
* **BUG** : à la bascule en consultation traduction du professeur / traduction de l’élève / traduction du professeur, on perd la transcription de référence !
* **BUG** : les alignements saisis par le professeur (transcription + traduction) ne sont pas enregistrés à la sauvegarde (perte de ces alignements au rechargement de la page).
* **BUG** : les alignements ne fonctionnent pas sur les vues non éditables : lorsqu’un élève consulte par exemple la transcription et la traduction de référence alignées par le professeur, cet alignement n’apparaît pas pour l’élève !
* Quand le professeur affiche le contenu de l’élève après avoir soumis sa transcription de référence, la transciption vide (celle de l’élève ?) s’affiche… Gênant : afficher plutôt la transcription de référence identifiée comme telle : utile notamment pour le professeur à la consultation des traductions soumises par les élèves !
* Quid de la *date limite de modification* ? Uniquement de transcription ? ou des modifications possibles ? Le professeur doit-il redéfinir cette date à chaque étape du processus (transcription, traduction, commentaire) ?


### <a name="facsim"></a>Facsimilé
`@role: ?`  
**Un professeur (/ un utilisateur désigné ?) aligne la transcription à l’image du document.**

#### Scénario
1. Dans la visionneuse (Leaflet), l’utilisateur détoure des zones d’images.
1. Dans la fenêtre de la transcription, l’utilisateur sélectionne (surligne) un extrait.
1. Grâce au bouton au-dessus de la transcription, l’utilisateur lie l’extrait sélectionné (surligné) à une zone d’image en la sélectionnant dans le menu déroulant qui apparaît.


#### L’utilisateur définit des zones d’image.
1. Cliquer sur le bouton correspondant au type de zone souhaité ;
  * rectangle : bouton `Ajouter un rectangle`
  * polygone : bouton `Ajouter un polygone`
  * cercle :  bouton `Ajouter un cercle`
1. tracer la zone sur l’image ;
1. éventuellement la reprendre (déplacement, déformation) ;
1. définir autant de zones que souhaité ;
1. cliquer sur le bouton `Sauvegarder les zones de la page en cours` pour enregistrer les zones.

#### L’utilisateur affiche/masque les zones d’images déjà définies.
* Cliquer sur le bouton `Afficher les zones`.

#### L’utilisateur supprime des zones d’images déjà définies.
1. Cliquer sur le bouton `Supprimer une zone` (quand la fonctionnalité est active, le bouton est mis en valeur en bleu) ;
1. cliquer sur les zones à supprimer ;
1. cliquer sur  le bouton `Sauvegarder les zones de la page en cours` pour enregistrer les suppressions.

NB : tant que l’utilisateur n’a pas cliqué sur ce bouton `Sauvegarder les zones de la page en cours`, il peut récupérer les zones supprimées en cliquant sur le bouton `Recharger la page en cours`.

#### L’utilisateur lie une portion de la transcription à une zone d’image prédéfinie.
1. Surligner à la souris une portion de texte  
  NB : garder cette sélection active : le surligenemnt doit être visible à l’écran ;
1. cliquer sur le bouton `Lier` ;
1. sélectionner dans le menu déroulant qui apparaît la zone d’image à lier ;
1. cliquer sur `Valider` ;
1. penser à cliquer sur `Sauvegarder les changements`.

NB : le texte de la transcription, apparaît au survol de la zone correspondante de l’image.

#### L’utilisateur supprime un alignement texte/image.
1. Cliquer sur la zone colorée de la transcription que l’on souhaite délier de la portion d’image ;
1. Dans le menu contectuel qui apparaît, cliquer sur `Supprimer`, puis sur `Oui je veux le supprimer`.


#### Bugs, remarques
* **Bug** : les zones définies dans l’image n’apparaîssent pas dans le menu déroulant côté texte (l’utilisateur ne peut pas visualiser le fragment d’image à lier au texte sélectionné).
* **Bug** : la suppression de l’alignement ne fonctionne pas.
* En l’état, un élève ne peut pas aligner la transcription à l’image (la transcription de référence n’apparaît pas dans la fenêtre d’alignement…).
* Question : travail réservé au professeur ? -> **plutôt oui**.


### <a name="speech"></a>Parties du discours
`@role: student, teacher`  
**Segmentation de la transcription de référence en parties du discours (définitions du VID).**

#### Scénario
1. L’élève segmente et annote la transcription de référence ;
1. Le professeur consulte la segmentation proposée par les élèves ;
1. Le professeur segmente lui-même OU clone la segmentation de l’élève de son choix ;
1. Le professeur publie sa segmentation de référence.

#### L’utilisateur lie une portion de la transcription à un type de partie du discours.
1. Dans l’onglet `Parties du discours` de la fenêtre d’édition, surligner à la souris une portion de texte  
  NB : garder cette sélection active : le surligenemnt doit être visible à l’écran ;
1. cliquer sur le bouton `Parties du discours` ;
1. sélectionner dans le menu déroulant `Type`, le type souhaité (*adresse*, *suscription*, etc.) ;
1. saisir un court commentaire optionnel pour décrire plus finement la partie du discours catégorisée ;
1. cliquer sur `Valider` ;
1. **penser à cliquer sur `Sauvegarder les changements`.**

#### L’utilisateur délie une portion de la transcription à un type de partie du discours.
1. Cliquer sur la zone colorée de la transcription que l’on souhaite délier de la partie du discours ;
1. Dans le menu contextuel qui apparaît, cliquer sur `Supprimer la partie du discours`, puis sur `Oui je veux la supprimer` ;
1. **penser à cliquer sur `Sauvegarder les changements`.**

#### Bugs, remarques
* **Bug** : les boutons de mise en forme typo du commentaire provoque le rechargement du document (et donc la perte de l’annotation produite…)
* **Bug** : pour la suppression, bug de sélection de la portion de texte à saisir (on ne parvient pas à sélectionner l’intégralié de la partie du discours annotée).
* En l’état, un élève ne peut pas saisir de partie du discours (la transcription de référence n’apparaît pas dans la fenêtre d’édition des parties du discours…).


### <a name="comment"></a>Commentaires
`@role: student, teacher`

#### Scénario
1. L’élève rédige des commentaires ;
1. Le professeur consulte les commentaires rédigés par les élèves ;
1. Le professeur rédige ses commentaires OU clone et corrige des commentaires d’élèves ;
1. Le professeur publie les commentaires de référence.

#### <a name="comment_edit"></a>L’élève édite des commentaires.
* Dans l’onglet `Commentaires` de la fenêtre d’édition du document, sélectionner le type de commentaire souhaité (`Diplomatique`, `Historique`, `Juridique`, etc.) ;
* Pour chaque commentaire, un onglet se crée dans la fenêtre d’édition ;
* Saisir les commentaires et penser à `Enregistrer les modifications`.

#### L’élève supprime un commentaire.
**TODO**

#### Le professeur clone des commentaires.
Le professeur peut cloner un commentaire spécifique (diplomatique, historique, etc.) de chaque élève.
**TODO**
