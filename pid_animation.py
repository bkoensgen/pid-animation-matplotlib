import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.font_manager as fm
from matplotlib.patches import FancyArrowPatch, Polygon

# --- Configuration ---
POINT_CONSIGNE = 5.0
POS_INITIALE = 0.0
DUREE_SIM_PHASE = 9
DT = 0.05
FPS = 30
FRAMES_PAUSE = 50  # Légèrement plus long pour les transitions animées
FRAMES_FONDU_TEXTE = 15 # Pour les textes et la courbe
FRAMES_TRANSITION_TITRE = 20 # Pour le glissement du titre

# --- Système ---
class Systeme:
    def __init__(self, pos_initiale=POS_INITIALE, masse=1.0, amortissement=0.25):
        self.position = pos_initiale
        self.vitesse = 0.0
        self.masse = masse
        self.amortissement = amortissement

    def maj(self, force_controle, dt):
        force_effective = force_controle - self.amortissement * self.vitesse
        acceleration = force_effective / self.masse
        self.vitesse += acceleration * dt
        self.position += self.vitesse * dt
        return self.position, self.vitesse

    def reinit(self, pos_initiale=POS_INITIALE):
        self.position = pos_initiale
        self.vitesse = 0.0

# --- Contrôleur PID ---
class ControleurPID:
    def __init__(self, Kp, Ki, Kd, point_consigne, dt, limites_integrale=(-12, 12), limites_sortie=(-18, 18)):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.point_consigne = point_consigne
        self.dt = dt
        self.integrale = 0
        self.erreur_precedente = 0
        self.integrale_min, self.integrale_max = limites_integrale
        self.sortie_min, self.sortie_max = limites_sortie

    def calculer(self, valeur_actuelle, vitesse_actuelle):
        erreur = self.point_consigne - valeur_actuelle
        terme_p_force = self.Kp * erreur
        self.integrale += erreur * self.dt
        self.integrale = np.clip(self.integrale, self.integrale_min, self.integrale_max)
        terme_i_force = self.Ki * self.integrale
        derivee_erreur = (erreur - self.erreur_precedente) / self.dt
        terme_d_force = self.Kd * derivee_erreur
        self.erreur_precedente = erreur
        signal_controle = terme_p_force + terme_i_force + terme_d_force
        signal_controle = np.clip(signal_controle, self.sortie_min, self.sortie_max)
        return signal_controle, erreur, terme_p_force, terme_i_force, terme_d_force

    def reinit(self):
        self.integrale = 0
        self.erreur_precedente = 0

# --- Esthétique & Setup ---
try:
    nom_police = "Roboto Condensed"
    chemin_police = fm.findfont(fm.FontProperties(family=nom_police))
    plt.rcParams['font.family'] = fm.FontProperties(fname=chemin_police).get_name()
except Exception:
    try:
        nom_police = "DejaVu Sans"
        chemin_police = fm.findfont(fm.FontProperties(family=nom_police))
        plt.rcParams['font.family'] = fm.FontProperties(fname=chemin_police).get_name()
        print(f"Police '{nom_police}' non trouvée, fallback sur 'DejaVu Sans'.")
    except Exception as e_fallback:
        print(f"Aucune police de fallback trouvée non plus: {e_fallback}")

plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(12.8, 7.2))

systeme_sim = Systeme(pos_initiale=POS_INITIALE)
temps_points_phase = np.arange(0, DUREE_SIM_PHASE, DT)
nb_frames_phase = len(temps_points_phase)

configs_pid = [
    {'nom': 'Contrôleur P', 'Kp': 1.2, 'Ki': 0.0, 'Kd': 0.0, 'couleur': '#FF6B6B',
     'desc': "Réagit à l'erreur actuelle ($K_p \cdot e$)\nLaisse souvent une erreur statique."},
    {'nom': 'Contrôleur PI', 'Kp': 1.0, 'Ki': 0.5, 'Kd': 0.0, 'couleur': '#4ECDC4',
     'desc': "Ajoute l'action intégrale ($K_i \int e \, dt$)\nÉlimine l'erreur statique, peut dépasser."},
    {'nom': 'Contrôleur PID', 'Kp': 1.8, 'Ki': 0.7, 'Kd': 2.2, 'couleur': '#45B7D1',
     'desc': "PID complet (action dérivée $K_d \\frac{de}{dt}$)\nRapide, stable, sans erreur statique (idéal)."}
]

frames_par_cycle = nb_frames_phase + FRAMES_PAUSE
total_frames = frames_par_cycle * len(configs_pid) - FRAMES_PAUSE

# --- Pré-calcul des Limites Y par Phase ---
limites_y_phase = {}
POS_Y_TITRE_AXES_FINAL = 0.93
POS_Y_DESC_AXES_FINAL = 0.15
MAX_DATA_Y_AXES_FRACTION = 0.87
POURCENTAGE_BUFFER_Y = 0.10

print("Pré-calcul des limites Y pour chaque phase...")
for i, config in enumerate(configs_pid):
    systeme_sim.reinit(POS_INITIALE)
    pid_sim = ControleurPID(config['Kp'], config['Ki'], config['Kd'], POINT_CONSIGNE, DT)
    donnees_y_phase = [POS_INITIALE]
    for _ in temps_points_phase:
        controle, _, _, _, _ = pid_sim.calculer(systeme_sim.position, systeme_sim.vitesse)
        pos, _ = systeme_sim.maj(controle, DT)
        donnees_y_phase.append(pos)
    min_val_sim = min(donnees_y_phase); max_val_sim = max(donnees_y_phase)
    ymin_phase = min(POS_INITIALE, POINT_CONSIGNE, min_val_sim)
    ymin_phase -= abs(max_val_sim - ymin_phase) * POURCENTAGE_BUFFER_Y 
    if abs(ymin_phase - max_val_sim) < 1e-3 : ymin_phase -= 1 
    if abs(max_val_sim - ymin_phase) < 1e-3 : 
        ymax_phase_donnees = max_val_sim + 1.0 
    else:
        ymax_phase_donnees = ymin_phase + (max_val_sim - ymin_phase) / MAX_DATA_Y_AXES_FRACTION
    ymax_phase_consigne = POINT_CONSIGNE + abs(POINT_CONSIGNE - ymin_phase) * POURCENTAGE_BUFFER_Y
    if abs(ymax_phase_consigne - ymin_phase) < 1e-3 : ymax_phase_consigne +=1
    ymax_phase = max(ymax_phase_donnees, ymax_phase_consigne, max_val_sim + 0.5) 
    limites_y_phase[i] = (ymin_phase, ymax_phase)
print("Pré-calcul terminé.")

# --- Éléments Graphiques ---
ligne_pos, = ax.plot([], [], '-', lw=4, label='Sortie Système', zorder=10, solid_capstyle='round')
ligne_consigne = ax.axhline(POINT_CONSIGNE, color='w', lw=2.5, ls=':', label=f'Consigne ({POINT_CONSIGNE})', zorder=5)
patch_remplissage_erreur = Polygon([[0,0]], closed=True, alpha=0.25, edgecolor=None, zorder=1, visible=False)
ax.add_patch(patch_remplissage_erreur)

ECHELLE_FLECHE_FORCE = 0.25
fleche_force_controle = FancyArrowPatch((0,0), (0,0), mutation_scale=20, arrowstyle='-|>', 
                                      lw=2.5, alpha=0.0, zorder=12, visible=False) # Alpha initial à 0
ax.add_patch(fleche_force_controle)

# Textes - positions initiales pour animation de glissement
POS_Y_TITRE_AXES_INITIAL = POS_Y_TITRE_AXES_FINAL + 0.1 # Commence au-dessus
POS_Y_DESC_AXES_INITIAL = POS_Y_DESC_AXES_FINAL - 0.1   # Commence en-dessous

texte_titre_principal = ax.text(0.5, POS_Y_TITRE_AXES_INITIAL, '', transform=ax.transAxes, ha='center', va='center',
                           fontsize=38, fontweight='bold', color='white', alpha=0.0,
                           bbox=dict(boxstyle="round,pad=0.3", fc="#202020", ec="None", alpha=0.0))

texte_description = ax.text(0.5, POS_Y_DESC_AXES_INITIAL, '', transform=ax.transAxes, ha='center', va='center',
                    fontsize=16, color='lightgrey', wrap=True, alpha=0.0, linespacing=1.4,
                    multialignment='center')

affichage_temps = ax.text(0.98, 0.03, '', transform=ax.transAxes, ha='right', va='bottom',
                       fontsize=14, color='lightgrey')
affichage_transition = ax.text(0.5, 0.55, '', transform=ax.transAxes, ha='center', va='center',
                               fontsize=32, fontweight='bold', color='black', alpha=0.0,
                               bbox=dict(boxstyle="round,pad=0.8", fc="gold", alpha=0.0), zorder=20)

historique_x, historique_y = [], []
idx_phase_actuelle = -1
controleur_pid_principal = ControleurPID(0,0,0, POINT_CONSIGNE, DT)
temps_global_actuel = 0.0

# --- Fonctions d'Animation ---
def ease_out_quad(t): return 1 - (1 - t) * (1 - t)
def ease_in_out_quad(t): return 2*t*t if t < 0.5 else 1 - pow(-2*t + 2, 2) / 2

def animer_proprietes_texte(obj_texte, target_alpha, target_y, current_y, frame_count, total_frames, ease_func=ease_out_quad):
    # Animation pour l'alpha et la position Y
    progress = frame_count / total_frames if total_frames > 0 else 1.0
    eased_progress = ease_func(progress)

    # Alpha
    current_alpha = obj_texte.get_alpha()
    if abs(current_alpha - target_alpha) > 1e-2 or (target_alpha == 0 and current_alpha != 0) or (target_alpha == 1 and current_alpha !=1): # Forcer si cible est 0 ou 1
        new_alpha = current_alpha + (target_alpha - current_alpha) * eased_progress # Interpolation
        obj_texte.set_alpha(np.clip(new_alpha, 0, 1))

    # Position Y
    if abs(current_y - target_y) > 1e-3:
        new_y = current_y + (target_y - current_y) * eased_progress # Interpolation
        obj_texte.set_y(new_y)
    else:
        obj_texte.set_y(target_y) # Snap to target if close

    # Bbox (si existe)
    bbox = obj_texte.get_bbox_patch()
    if bbox:
        current_bbox_alpha = bbox.get_alpha()
        if obj_texte == texte_titre_principal: target_bbox_alpha = target_alpha * 0.6 
        elif obj_texte == affichage_transition: target_bbox_alpha = target_alpha * 0.85
        else: target_bbox_alpha = 0 
        if abs(current_bbox_alpha - target_bbox_alpha) > 1e-2 or (target_bbox_alpha == 0 and current_bbox_alpha != 0) or (target_bbox_alpha > 0.8 and current_bbox_alpha < 0.8):
            new_bbox_alpha = current_bbox_alpha + (target_bbox_alpha - current_bbox_alpha) * eased_progress
            bbox.set_alpha(np.clip(new_bbox_alpha, 0, 1))

def init():
    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.08, top=0.90) 
    ax.set_xlim(-0.05 * DUREE_SIM_PHASE, DUREE_SIM_PHASE * 1.05)
    ax.set_xlabel('Temps (s)', fontsize=16, color='lightgrey', labelpad=10)
    ax.set_ylabel('Sortie Système', fontsize=16, color='lightgrey', labelpad=10)
    ax.legend(loc='upper right', fontsize=12, framealpha=0.6, facecolor='#2A2A2A', edgecolor='None', labelcolor='white')
    ax.tick_params(axis='both', which='major', labelsize=12, colors='lightgrey')
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.3)
    fig.patch.set_facecolor('#2A2A2A') 
    ax.set_facecolor('#333333')       

    ligne_pos.set_data([], []); ligne_pos.set_alpha(1.0)
    patch_remplissage_erreur.set_visible(False)
    fleche_force_controle.set_visible(False); fleche_force_controle.set_alpha(0.0)
    
    texte_titre_principal.set_alpha(0.0); texte_titre_principal.set_y(POS_Y_TITRE_AXES_INITIAL)
    if texte_titre_principal.get_bbox_patch(): texte_titre_principal.get_bbox_patch().set_alpha(0.0)
    texte_description.set_alpha(0.0); texte_description.set_y(POS_Y_DESC_AXES_INITIAL)
    
    affichage_temps.set_text('')
    affichage_transition.set_alpha(0.0); affichage_transition.set_y(0.55) # Position fixe
    if affichage_transition.get_bbox_patch(): affichage_transition.get_bbox_patch().set_alpha(0.0)
    
    return (ligne_pos, ligne_consigne, patch_remplissage_erreur, fleche_force_controle,
            texte_titre_principal, texte_description, affichage_temps, affichage_transition)

frame_count_transition = 0 # Compteur pour l'animation des textes

def maj_animation(frame):
    global idx_phase_actuelle, controleur_pid_principal, historique_x, historique_y 
    global temps_global_actuel, systeme_sim, frame_count_transition

    idx_phase_calcule = frame // frames_par_cycle
    frame_dans_cycle = frame % frames_par_cycle
    est_frame_pause = (frame_dans_cycle >= nb_frames_phase) and (idx_phase_calcule < len(configs_pid) - 1)
    est_frame_sim = not est_frame_pause and frame_dans_cycle < nb_frames_phase
    
    # --- Animation des textes et de la courbe (alpha/position) ---
    if est_frame_sim:
        frame_count_transition += 1
        # Titre: Glisse du haut et apparaît
        animer_proprietes_texte(texte_titre_principal, 1.0, POS_Y_TITRE_AXES_FINAL, texte_titre_principal.get_y(), frame_count_transition, FRAMES_TRANSITION_TITRE)
        # Description: Glisse du bas et apparaît
        animer_proprietes_texte(texte_description, 1.0, POS_Y_DESC_AXES_FINAL, texte_description.get_y(), frame_count_transition, FRAMES_TRANSITION_TITRE)
        # Transition: Disparaît (si elle était visible)
        animer_proprietes_texte(affichage_transition, 0.0, 0.55, affichage_transition.get_y(), frame_count_transition, FRAMES_FONDU_TEXTE)
        ligne_pos.set_alpha(1.0) # S'assurer que la ligne est visible
        fleche_force_controle.set_alpha(0.85 if fleche_force_controle.get_visible() else 0.0) # Fondu de la flèche

    elif est_frame_pause:
        frame_count_transition +=1 # Continue pour le fondu sortant / entrant de la transition
        # Titre et description de la phase précédente: Glissent et disparaissent
        animer_proprietes_texte(texte_titre_principal, 0.0, POS_Y_TITRE_AXES_INITIAL, texte_titre_principal.get_y(), frame_count_transition, FRAMES_TRANSITION_TITRE)
        animer_proprietes_texte(texte_description, 0.0, POS_Y_DESC_AXES_INITIAL, texte_description.get_y(), frame_count_transition, FRAMES_TRANSITION_TITRE)
        # Texte de transition: Apparaît
        animer_proprietes_texte(affichage_transition, 1.0, 0.55, affichage_transition.get_y(), frame_count_transition, FRAMES_FONDU_TEXTE)
        # Estomper la courbe précédente
        current_alpha_ligne = ligne_pos.get_alpha()
        if current_alpha_ligne > 0.1: ligne_pos.set_alpha(current_alpha_ligne * 0.85) # Diminution progressive
        fleche_force_controle.set_alpha(0.0) # Cacher la flèche pendant la pause


    # --- Changement de Phase ---
    if idx_phase_calcule != idx_phase_actuelle and idx_phase_calcule < len(configs_pid):
        idx_phase_actuelle = idx_phase_calcule
        config = configs_pid[idx_phase_actuelle]
        frame_count_transition = 0 # Réinitialiser le compteur pour la nouvelle phase

        ax.set_ylim(limites_y_phase[idx_phase_actuelle]) 
        systeme_sim.reinit(POS_INITIALE) 
        controleur_pid_principal.Kp, controleur_pid_principal.Ki, controleur_pid_principal.Kd = config['Kp'], config['Ki'], config['Kd']
        controleur_pid_principal.reinit()
        historique_x.clear(); historique_y.clear() # Effacer l'historique pour la nouvelle courbe
        
        ligne_pos.set_data([], []) # Important pour redémarrer la courbe
        ligne_pos.set_color(config['couleur']); ligne_pos.set_alpha(1.0) # Nouvelle courbe alpha = 1
        
        patch_remplissage_erreur.set_facecolor(config['couleur'])
        fleche_force_controle.set_color(config['couleur'])
        
        texte_titre_principal.set_text(config['nom']); texte_titre_principal.set_color(config['couleur'])
        texte_titre_principal.set_y(POS_Y_TITRE_AXES_INITIAL); texte_titre_principal.set_alpha(0.0) # Prêt pour animation entrante
        if texte_titre_principal.get_bbox_patch(): texte_titre_principal.get_bbox_patch().set_alpha(0.0)

        texte_description.set_text(config['desc'])
        texte_description.set_y(POS_Y_DESC_AXES_INITIAL); texte_description.set_alpha(0.0) # Prêt pour animation entrante
        
        affichage_transition.set_y(0.55); affichage_transition.set_alpha(0.0) # Prêt pour animation (si besoin)
        if affichage_transition.get_bbox_patch(): affichage_transition.get_bbox_patch().set_alpha(0.0)
        
        fleche_force_controle.set_visible(False); fleche_force_controle.set_alpha(0.0)

    # --- Logique de Pause (affichage message "Suivant") ---
    if est_frame_pause:
        if idx_phase_actuelle + 1 < len(configs_pid):
            prochaine_config = configs_pid[idx_phase_actuelle + 1]
            affichage_transition.set_text(f"Suivant : {prochaine_config['nom']}")
            affichage_transition.set_color(prochaine_config['couleur']) 
            if affichage_transition.get_bbox_patch():
                 affichage_transition.get_bbox_patch().set_facecolor(prochaine_config['couleur'])
        affichage_temps.set_text(f'{DUREE_SIM_PHASE:.1f}s (Pause)')
        patch_remplissage_erreur.set_visible(False)
        # La flèche est déjà gérée par le bloc d'animation de texte/courbe

    # --- Logique de Simulation ---
    elif est_frame_sim:
        temps_global_actuel = frame_dans_cycle * DT
        signal_controle, erreur, p, i, d = controleur_pid_principal.calculer(systeme_sim.position, systeme_sim.vitesse)
        nouvelle_pos, nouvelle_vel = systeme_sim.maj(signal_controle, DT)
        
        historique_x.append(temps_global_actuel)
        historique_y.append(nouvelle_pos) 
        ligne_pos.set_data(historique_x, historique_y)
        
        affichage_temps.set_text(f'{temps_global_actuel:4.1f}s')

        if len(historique_x) > 1:
            coords_x_remplissage = [historique_x[-2], temps_global_actuel, temps_global_actuel, historique_x[-2]]
            coords_y_remplissage = [POINT_CONSIGNE, POINT_CONSIGNE, nouvelle_pos, historique_y[-2]]
            patch_remplissage_erreur.set_xy(list(zip(coords_x_remplissage, coords_y_remplissage)))
            patch_remplissage_erreur.set_visible(True)
        else:
            patch_remplissage_erreur.set_visible(False)

        if abs(signal_controle) > 0.1:
            pos_x_fleche = temps_global_actuel - DT * 3 
            pos_y_depart_fleche = nouvelle_pos 
            ymin_actuel, ymax_actuel = ax.get_ylim()
            echelle_fleche_dynamique = ECHELLE_FLECHE_FORCE * (ymax_actuel - ymin_actuel) / 8.0
            pos_y_fin_fleche = nouvelle_pos + signal_controle * echelle_fleche_dynamique
            pos_y_fin_fleche_clampee = np.clip(pos_y_fin_fleche, ymin_actuel - 0.1*(ymax_actuel-ymin_actuel), ymax_actuel + 0.1*(ymax_actuel-ymin_actuel))
            fleche_force_controle.set_positions((pos_x_fleche, pos_y_depart_fleche), (pos_x_fleche, pos_y_fin_fleche_clampee))
            fleche_force_controle.set_visible(True) 
            # L'alpha de la flèche est géré dans le bloc d'animation des textes/courbes
        else:
            fleche_force_controle.set_visible(False)
            fleche_force_controle.set_alpha(0.0) # S'assurer qu'elle est transparente si non visible
            
    return (ligne_pos, ligne_consigne, patch_remplissage_erreur, fleche_force_controle,
            texte_titre_principal, texte_description, affichage_temps, affichage_transition)

# --- Création et Sauvegarde ---
print("Création de l'animation LinkedIn (transitions douces)...")
ani = FuncAnimation(fig, maj_animation, frames=total_frames,
                    init_func=init, blit=True, interval=1000/FPS, repeat=False)

try:
    ani.save('pid_linkedin_FR_v5_transitions.mp4', writer='ffmpeg', fps=FPS, dpi=180, 
             codec='libx264', extra_args=['-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '22'])
    print("Animation 'pid_linkedin_FR_v5_transitions.mp4' sauvegardée avec succès !")
except Exception as e:
    print(f"Erreur lors de la sauvegarde de l'animation : {e}")
    print("Assurez-vous que 'ffmpeg' est installé et dans votre PATH.")

# plt.show()
