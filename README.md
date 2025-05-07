# Animation de Contrôleur PID en Python avec Matplotlib

Ce dépôt contient le code Python permettant de générer une animation MP4 qui compare le comportement des contrôleurs Proportionnel (P), Proportionnel-Intégral (PI), et Proportionnel-Intégral-Dérivé (PID).

L'animation visualise la réponse d'un système simple à un changement de consigne pour chaque type de contrôleur, mettant en évidence les caractéristiques clés telles que l'erreur statique, le dépassement (overshoot), et le temps de stabilisation. Elle a été conçue avec un accent sur la clarté pédagogique, incluant des transitions fluides entre les phases et un ajustement dynamique des limites des axes.

## Fonctionnalités de l'animation

*   Comparaison visuelle des réponses des contrôleurs P, PI, et PID.
*   Affichage de la consigne, de la sortie du système, et de l'erreur.
*   Visualisation de la force de contrôle appliquée.
*   Transitions animées pour les titres, descriptions et changements de phase.
*   Ajustement automatique des limites de l'axe Y pour une visualisation optimale de chaque phase.
*   Code commenté en français (et anglais pour les termes techniques).

## Technologies utilisées

*   **Python 3.x**
*   **Matplotlib** : Pour le tracé des graphiques et la création de l'animation (`FuncAnimation`).
*   **NumPy** : Pour les calculs numériques et la manipulation de tableaux.
*   **FFmpeg** : Nécessaire pour sauvegarder l'animation au format MP4 (doit être installé séparément et accessible dans le PATH de votre système).

## Prérequis

Avant d'exécuter le script, assurez-vous d'avoir installé :

1.  Python 3.6 ou plus récent.
2.  Les bibliothèques Python requises :
    ```bash
    pip install numpy matplotlib
    ```
3.  FFmpeg : Suivez les instructions d'installation pour votre système d'exploitation sur [ffmpeg.org](https://ffmpeg.org/download.html).

## Utilisation

1.  Clonez ce dépôt :
    ```bash
    git clone https://github.com/bkoensgen/python-pid-animation.git
    ```

2.  Naviguez jusqu'au répertoire du projet :
    ```bash
    cd pid-animation-matplotlib
    ```

3.  Exécutez le script Python principal (par exemple, `pid_animation.py`) :
    ```bash
    python pid_animation.py
    ```

Le script générera un fichier vidéo MP4 dans le répertoire courant.

## Paramètres clés

Les principaux paramètres de la simulation et de l'animation peuvent être ajustés directement au début du script Python :

*   `POINT_CONSIGNE` : La valeur cible pour le système.
*   `POS_INITIALE` : La position de départ du système.
*   `DUREE_SIM_PHASE` : La durée de simulation pour chaque type de contrôleur.
*   Gains `Kp`, `Ki`, `Kd` pour chaque configuration de contrôleur dans `configs_pid`.
*   Paramètres d'animation comme `FPS`, `FRAMES_PAUSE`.

## Licence

Ce projet est distribué sous la licence MIT. 

---

N'hésitez pas à me contacter sur [LinkedIn](https://www.linkedin.com/in/benjamin-koensgen-6459711b1) si vous avez des questions ou des suggestions !
