
import pygame, random, os, database, sys


from controls import move_player
from classes.constants import WIDTH, HEIGHT, FPS, SHOOT_DELAY
from functions import show_game_over, music_background, show_game_win
from menu import show_menu, animate_screen

from classes.player import Player
from classes.bullets import Bullet
from classes.refill import BulletRefill, HealthRefill, DoubleRefill, ExtraScore
from classes.meteors import Meteors, Meteors2, BlackHole
from classes.explosions import Explosion, Explosion2
from classes.enemies import Enemy1, Enemy2
from classes.bosses import Boss1, Boss2, Boss3
from database import create_scores_table,save_score,get_highest_score,check_if_table_exists

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()
music_background()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surface = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE ATTACK")
clock = pygame.time.Clock()

def main():
    pygame.mixer.music.stop()
    pygame.mixer.music.load('Pygame/game_sounds/music.mp3')
    pygame.mixer.music.play(-1)
    animate_screen()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (64, 64, 64)

def get_name():
    """
    Permite al jugador ingresar su nombre después de haber obtenido un nuevo récord.
    """
    global name
    input_box = pygame.Rect(150, 400, 300, 40)
    name = ""
    is_typing = True

    while is_typing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    is_typing = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

        screen.fill(BLACK)

        # Configuración de la fuente y el tamaño del texto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "fonts", "PublicPixel.ttf")
        font_name = font_path
        font_size = 30
        font_size_dos = 12
        font = pygame.font.Font(font_name, font_size)
        font_dos = pygame.font.Font(font_name, font_size_dos)

        # Obtener el ancho y alto del texto
        text_width, text_height = font.size("New Record!")

        # Calcular las coordenadas para centrar el texto y la entrada de texto
        text_x = (WIDTH - text_width) // 2
        text_y = (HEIGHT - text_height) // 2 - 50

        input_box_x = (WIDTH - input_box.width) // 2
        input_box_y = (HEIGHT - input_box.height) // 2 + 50

        text = font.render("NEW RECORD!", True, WHITE)
        screen.blit(text, (text_x, text_y))

        text_surface = font_dos.render(name, True, WHITE)
        text_width = text_surface.get_width()  # Obtener el ancho del texto ingresado
        screen.blit(text_surface, (input_box_x + (input_box.width - text_width) // 2, input_box_y))  # Centrar el texto ingresado

        # Agregar una nueva línea de texto debajo de "NEW RECORD!"
        new_line_text = font_dos.render("↓ Ingresa tu nombre ↓", True, DARK_GRAY)
        new_line_text_x = (WIDTH - new_line_text.get_width()) // 2
        new_line_text_y = text_y + text_height + 20
        screen.blit(new_line_text, (new_line_text_x, new_line_text_y))

        pygame.display.flip()
        clock.tick(30)

explosions = pygame.sprite.Group()
explosions2 = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy1_group = pygame.sprite.Group()
enemy2_group = pygame.sprite.Group()
boss1_group = pygame.sprite.Group()
boss2_group = pygame.sprite.Group()
boss3_group = pygame.sprite.Group()
bullet_refill_group = pygame.sprite.Group()
health_refill_group = pygame.sprite.Group()
double_refill_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
meteor2_group = pygame.sprite.Group()
extra_score_group = pygame.sprite.Group()
black_hole_group = pygame.sprite.Group()
enemy2_bullets = pygame.sprite.Group()

boss1_bullets = pygame.sprite.Group()
boss2_bullets = pygame.sprite.Group()
boss3_bullets = pygame.sprite.Group()

boss1_health = 100
boss1_health_bar_rect = pygame.Rect(0, 0, 100, 5)
boss1_spawned = False

boss2_health = 100
boss2_health_bar_rect = pygame.Rect(0, 0, 100, 5)
boss2_spawned = False

boss3_health = 150
boss3_health_bar_rect = pygame.Rect(0, 0, 150, 5)
boss3_spawned = False

bg_y_shift = -HEIGHT
background_img = pygame.image.load('Pygame/images/bg/background.jpg').convert()
background_img2 = pygame.image.load('Pygame/images/bg/background2.png').convert()
background_img3 = pygame.image.load('Pygame/images/bg/background3.png').convert()
background_img4 = pygame.image.load('Pygame/images/bg/background4.png').convert()
background_top = background_img.copy()
current_image = background_img
new_background_activated = False

explosion_images = [pygame.image.load(f"Pygame/images/explosion/explosion{i}.png") for i in range(8)]
explosion2_images = [pygame.image.load(f"Pygame/images/explosion2/explosion{i}.png") for i in range(18)]
explosion3_images = [pygame.image.load(f"Pygame/images/explosion3/explosion{i}.png") for i in range(18)]

enemy1_img = [
    pygame.image.load('Pygame/images/enemy/enemy1_1.png').convert_alpha(),
    pygame.image.load('Pygame/images/enemy/enemy1_2.png').convert_alpha(),
    pygame.image.load('Pygame/images/enemy/enemy1_3.png').convert_alpha()
]
enemy2_img = [
    pygame.image.load('Pygame/images/enemy/enemy2_1.png').convert_alpha(),
    pygame.image.load('Pygame/images/enemy/enemy2_2.png').convert_alpha()
]
boss1_img = pygame.image.load('Pygame/images/boss/boss1.png').convert_alpha()
boss2_img = pygame.image.load('Pygame/images/boss/boss2_1.png').convert_alpha()
boss3_img = pygame.image.load('Pygame/images/boss/boss3.png').convert_alpha()

health_refill_img = pygame.image.load('Pygame/images/refill/health_refill.png').convert_alpha()
bullet_refill_img = pygame.image.load('Pygame/images/refill/bullet_refill.png').convert_alpha()
double_refill_img = pygame.image.load('Pygame/images/refill/double_refill.png').convert_alpha()

meteor_imgs = [
    pygame.image.load('Pygame/images/meteors/meteor_1.png').convert_alpha(),
    pygame.image.load('Pygame/images/meteors/meteor_2.png').convert_alpha(),
    pygame.image.load('Pygame/images/meteors/meteor_3.png').convert_alpha(),
    pygame.image.load('Pygame/images/meteors/meteor_4.png').convert_alpha()
]
meteor2_imgs = [
    pygame.image.load('Pygame/images/meteors/meteor2_1.png').convert_alpha(),
    pygame.image.load('Pygame/images/meteors/meteor2_2.png').convert_alpha(),
    pygame.image.load('Pygame/images/meteors/meteor2_3.png').convert_alpha(),
    pygame.image.load('Pygame/images/meteors/meteor2_4.png').convert_alpha()
]
extra_score_img = pygame.image.load('Pygame/images/score/score_coin.png').convert_alpha()
black_hole_imgs = [
    pygame.image.load('Pygame/images/hole/black_hole.png').convert_alpha(),
    pygame.image.load('Pygame/images/hole/black_hole2.png').convert_alpha()
]

initial_player_pos = (WIDTH // 2, HEIGHT - 100)
#crear db
create_scores_table()

################################SCORE#######################################
score = 25000
hi_score = 200000
#Comprobación si existe una tabla en la base de datos.
#Obtención del puntaje más alto si la tabla existe.
if check_if_table_exists():
    hi_score = get_highest_score()

#Obtención del nombre del puntaje más alto desde la base de datos.
hi_score_name = database.get_highscore_name()
name = hi_score_name

#Inicialización de variables relacionadas con el jugador, como vidas y contador de balas.
player = Player()
player_life = 500
bullet_counter = 500

#Variables booleanas para el estado del juego, como pausa y ejecución.
paused = False
running = True

if show_menu:
    import menu
    menu.main()

is_shooting = False
last_shot_time = 0

##########################BUCLE PRINCIPAL####################################
# Manejo de eventos de pygame, como presionar o soltar teclas.
#Control de movimiento del jugador.
#Control de disparo del jugador.
#Actualización de la posición de los elementos en el juego, como el fondo, los enemigos, los proyectiles y las explosiones.
#Colisiones entre los objetos del juego y el jugador o los proyectiles.
#Actualización de la puntuación y otros elementos del juego.
#Dibujo de los elementos en la pantalla.

while running:
    """
    El juego se ejecuta en un ciclo while.
    Se manejan los eventos del juego, se actualizan los sprites, 
    se verifica si el jugador pierde, se dibujan los elementos en la pantalla 
    """


    # Eventos del juego
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #Si se presiona la tecla de espacio y el juego no está pausado, se crea un objeto de bala y se agrega al grupo de balas.
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not paused:
                if bullet_counter > 0 and pygame.time.get_ticks() - last_shot_time > SHOOT_DELAY:
                    last_shot_time = pygame.time.get_ticks()
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullets.add(bullet)
                    bullet_counter -= 1
                is_shooting = True

            #Si se presiona la tecla de escape, se sale del juego.
            #Si se presiona la tecla "P" o "PAUSE", se pausa o reanuda el juego.
            #Si el juego no está pausado, se mueve al jugador en la dirección correspondiente según las teclas presionadas.
            elif event.key == pygame.K_ESCAPE:
                sys.exit(0)
            elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                paused = not paused
            elif not paused:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()
                elif event.key == pygame.K_UP:
                    player.move_up()
                elif event.key == pygame.K_DOWN:
                    player.move_down()

        #Se actualiza el estado de disparo del jugador.
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and player.original_image is not None:
                player.image = player.original_image.copy()
                is_shooting = False
            elif not paused:
                if event.key == pygame.K_LEFT:
                    player.stop_left()
                elif event.key == pygame.K_RIGHT:
                    player.stop_right()
                elif event.key == pygame.K_UP:
                    player.stop_up()
                elif event.key == pygame.K_DOWN:
                    player.stop_down()

     #Se comprueba si ha pasado el tiempo suficiente desde el último disparo y se dispara una bala si el jugador está disparando.
    if pygame.time.get_ticks() - last_shot_time > SHOOT_DELAY and is_shooting and not paused:
        if bullet_counter > 0:
            last_shot_time = pygame.time.get_ticks()
            bullet = Bullet(player.rect.centerx, player.rect.top)
            bullets.add(bullet)
            bullet_counter -= 1
    #Si el juego está pausado, se muestra el mensaje "PAUSE" en la pantalla.
    if paused:
        font = pygame.font.SysFont('Comic Sans MS', 40)
        text = font.render("PAUSE", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()

    if not paused:
        move_player(keys, player)

        screen.blit(current_image, (0, bg_y_shift))
        background_top_rect = background_top.get_rect(topleft=(0, bg_y_shift))
        background_top_rect.top = bg_y_shift + HEIGHT
        screen.blit(background_top, background_top_rect)

    bg_y_shift += 1
    if bg_y_shift >= 0:
        bg_y_shift = -HEIGHT

    if score > 1000:
        bg_y_shift += 2

    if score >= 1000 and not new_background_activated:
        current_image = background_img2
        background_top = background_img2.copy()
        new_background_activated = True

    if score >= 10000 and new_background_activated:
        current_image = background_img3
        background_top = background_img3.copy()

    if score >= 15000 and new_background_activated:
        current_image = background_img4
        background_top = background_img4.copy()

    if score == 0:
        current_image = background_img
        background_top = background_img.copy()
        new_background_activated = False

    screen.blit(current_image, (0, bg_y_shift))
    background_top_rect = background_top.get_rect(topleft=(0, bg_y_shift))
    background_top_rect.top = bg_y_shift + HEIGHT
    screen.blit(background_top, background_top_rect)

    #Se generan enemigos y obstáculos aleatorios en función de la puntuación obtenida.
    if score > hi_score: 
        hi_score = score

    if random.randint(0, 120) == 0:
        enemy_img = random.choice(enemy1_img)
        enemy_object = Enemy1(
            random.randint(100, WIDTH - 50),
            random.randint(-HEIGHT, -50),
            enemy_img,
        )
        enemy1_group.add(enemy_object)

    if score >= 3000 and random.randint(0, 40) == 0 and len(enemy2_group) < 2:
        enemy_img = random.choice(enemy2_img)
        enemy2_object = Enemy2(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            enemy_img,
        )
        enemy2_group.add(enemy2_object)

    if score >= 5000 and not boss1_spawned:
        pygame.mixer.Sound('Pygame/game_sounds/warning.mp3').play()
        boss1_img = boss1_img
        boss1_object = Boss1(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss1_img,
        )
        boss1_group.add(boss1_object)
        boss1_spawned = True

    if score >= 10000 and not boss2_spawned:
        pygame.mixer.Sound('Pygame/game_sounds/warning.mp3').play()
        boss2_img = boss2_img
        boss2_object = Boss2(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss2_img,
        )
        boss2_group.add(boss2_object)
        boss2_spawned = True

    if score >= 15000 and not boss3_spawned:
        pygame.mixer.Sound('Pygame/game_sounds/warning.mp3').play()
        boss3_img = boss3_img
        boss3_object = Boss3(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss3_img,
        )
        boss3_group.add(boss3_object)
        boss3_spawned = True

    if random.randint(0, 60) == 0:
        extra_score = ExtraScore(
            random.randint(50, WIDTH - 50),
            random.randint(-HEIGHT, -50 - extra_score_img.get_rect().height),
            extra_score_img,
        )

        extra_score_group.add(extra_score)

    if score > 3000 and random.randint(0, 100) == 0:
        meteor_img = random.choice(meteor_imgs)
        meteor_object = Meteors(
            random.randint(0, 50),
            random.randint(0, 50),
            meteor_img,
        )
        meteor_group.add(meteor_object)

    if random.randint(0, 90) == 0:
        meteor2_img = random.choice(meteor2_imgs)
        meteor2_object = Meteors2(
            random.randint(100, WIDTH - 50),
            random.randint(-HEIGHT, -50 - meteor2_img.get_rect().height),
            meteor2_img,
        )
        meteor2_group.add(meteor2_object)

    if score > 1000 and random.randint(0, 500) == 0:
        black_hole_img = random.choice(black_hole_imgs)
        black_hole_object = BlackHole(
            random.randint(100, WIDTH - 50),
            random.randint(-HEIGHT, -50 - black_hole_img.get_rect().height),
            black_hole_img,
        )
        black_hole_group.add(black_hole_object)

##########################CONTROL FIN DE JUEGO###########################
#Verificación de la vida del jugador.
#Mostrar pantalla de juego terminado.
#Reiniciar variables y grupos de elementos del juego.

    if player_life <= 0:
        if score >= hi_score:
            get_name()
            save_score(name, score)
        show_game_over(screen, score)
        boss1_spawned = False
        boss1_health = 150
        boss2_spawned = False
        boss2_health = 150
        boss3_spawned = False
        boss3_health = 200
        score = 0
        player_life = 200
        bullet_counter = 200
        player.rect.topleft = initial_player_pos
        bullets.empty()
        bullet_refill_group.empty()
        health_refill_group.empty()
        double_refill_group.empty()
        extra_score_group.empty()
        black_hole_group.empty()
        meteor_group.empty()
        meteor2_group.empty()
        enemy1_group.empty()
        enemy2_group.empty()
        boss1_group.empty()
        boss2_group.empty()
        boss3_group.empty()
        explosions.empty()
        explosions2.empty()

    for black_hole_object in black_hole_group:
        black_hole_object.update()
        black_hole_object.draw(screen)

        if black_hole_object.rect.colliderect(player.rect):
            player_life -= 1
            black_hole_object.sound_effect.play()

        if score >= 5000:
            meteor_object.speed = 2
        if score >= 10000:
            meteor_object.speed = 4
        if score >= 15000:
            meteor_object.speed = 6
        if score >= 20000:
            meteor_object.speed = 8

    for bullet_refill in bullet_refill_group:

        bullet_refill.update()
        bullet_refill.draw(screen)

        if player.rect.colliderect(bullet_refill.rect):
            if bullet_counter < 200:
                bullet_counter += 50
                if bullet_counter > 200:
                    bullet_counter = 200
                bullet_refill.kill()
                bullet_refill.sound_effect.play()
            else:
                bullet_refill.kill()
                bullet_refill.sound_effect.play()

    for health_refill in health_refill_group:
        health_refill.update()
        health_refill.draw(screen)

        if player.rect.colliderect(health_refill.rect):
            if player_life < 200:
                player_life += 50
                if player_life > 200:
                    player_life = 200
                health_refill.kill()
                health_refill.sound_effect.play()
            else:
                health_refill.kill()
                health_refill.sound_effect.play()

    for extra_score in extra_score_group:
        extra_score.update()
        extra_score.draw(screen)

        if player.rect.colliderect(extra_score.rect):
            score += 20
            extra_score.kill()
            extra_score.sound_effect.play()

        if score >= 3000:
            extra_score.speed = 2
        if score >= 10000:
            extra_score.speed = 4
        if score >= 15000:
            extra_score.speed = 6
        if score >= 20000:
            extra_score.speed = 8

    for double_refill in double_refill_group:
        double_refill.update()
        double_refill.draw(screen)

        if player.rect.colliderect(double_refill.rect):
            if player_life < 200:
                player_life += 50
                if player_life > 200:
                    player_life = 200
            if bullet_counter < 200:
                bullet_counter += 50
                if bullet_counter > 200:
                    bullet_counter = 200
                double_refill.kill()
                double_refill.sound_effect.play()
            else:
                double_refill.kill()
                double_refill.sound_effect.play()

    #Actualización y dibujo de elementos adicionales:
        #Actualización y dibujo de elementos como meteoritos, refuerzos de vida y puntuación adicional.
        #Actualización y dibujo de jefes en el juego.
    for meteor_object in meteor_group:
        meteor_object.update()
        meteor_object.draw(screen)

        if meteor_object.rect.colliderect(player.rect):
            player_life -= 10
            explosion = Explosion(meteor_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor_object.kill()
            score += 50

        bullet_collisions = pygame.sprite.spritecollide(meteor_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion = Explosion(meteor_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor_object.kill()
            score += 80

            if random.randint(0, 10) == 0:
                double_refill = DoubleRefill(
                    meteor_object.rect.centerx,
                    meteor_object.rect.centery,
                    double_refill_img,
                )
                double_refill_group.add(double_refill)

        if score >= 3000:
            meteor_object.speed = 2
        if score >= 10000:
            meteor_object.speed = 4
        if score >= 15000:
            meteor_object.speed = 6
        if score >= 20000:
            meteor_object.speed = 8

    for meteor2_object in meteor2_group:
        meteor2_object.update()
        meteor2_object.draw(screen)

        if meteor2_object.rect.colliderect(player.rect):
            player_life -= 10
            explosion = Explosion(meteor2_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor2_object.kill()
            score += 20

        #Se detectan colisiones entre los elementos del juego, como el jugador con los enemigos o las balas con los enemigos.
        bullet_collisions = pygame.sprite.spritecollide(meteor2_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion = Explosion(meteor2_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor2_object.kill()
            score += 40

            if random.randint(0, 20) == 0:
                double_refill = DoubleRefill(
                    meteor2_object.rect.centerx,
                    meteor2_object.rect.centery,
                    double_refill_img,
                )
                double_refill_group.add(double_refill)

        if score >= 3000:
            meteor2_object.speed = 2
        if score >= 10000:
            meteor2_object.speed = 4
        if score >= 15000:
            meteor2_object.speed = 6
        if score >= 20000:
            meteor2_object.speed = 8

    for enemy_object in enemy1_group:
        enemy_object.update(enemy1_group)
        enemy1_group.draw(screen)

        if enemy_object.rect.colliderect(player.rect):
            player_life -= 10
            explosion = Explosion(enemy_object.rect.center, explosion_images)
            explosions.add(explosion)
            enemy_object.kill()
            score += 20

        bullet_collisions = pygame.sprite.spritecollide(enemy_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion = Explosion(enemy_object.rect.center, explosion_images)
            explosions.add(explosion)
            enemy_object.kill()
            score += 50

            if random.randint(0, 8) == 0:
                bullet_refill = BulletRefill(
                    enemy_object.rect.centerx,
                    enemy_object.rect.centery,
                    bullet_refill_img,
                )
                bullet_refill_group.add(bullet_refill)

            if random.randint(0, 8) == 0:
                health_refill = HealthRefill(
                    random.randint(50, WIDTH - 30),
                    random.randint(-HEIGHT, -30),
                    health_refill_img,
                )
                health_refill_group.add(health_refill)

    for enemy2_object in enemy2_group:
        enemy2_object.update(enemy2_group, enemy2_bullets, player)
        enemy2_group.draw(screen)
        enemy2_bullets.update()
        enemy2_bullets.draw(screen)

        if enemy2_object.rect.colliderect(player.rect):
            player_life -= 40
            explosion2 = Explosion2(enemy2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            enemy2_object.kill()
            score += 20

        bullet_collisions = pygame.sprite.spritecollide(enemy2_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion2(enemy2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            enemy2_object.kill()
            score += 80

            if random.randint(0, 20) == 0:
                double_refill = DoubleRefill(
                    enemy2_object.rect.centerx,
                    enemy2_object.rect.centery,
                    double_refill_img,
                )
                double_refill_group.add(double_refill)

        for enemy2_bullet in enemy2_bullets:
            if enemy2_bullet.rect.colliderect(player.rect):
                player_life -= 10
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                enemy2_bullet.kill()

    for boss1_object in boss1_group:
        boss1_object.update(boss1_bullets, player)
        boss1_group.draw(screen)
        boss1_bullets.update()
        boss1_bullets.draw(screen)

        if boss1_object.rect.colliderect(player.rect):
            player_life -= 20
            explosion = Explosion2(boss1_object.rect.center, explosion2_images)
            explosions2.add(explosion)

        bullet_collisions = pygame.sprite.spritecollide(boss1_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion(boss1_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            boss1_health -= 5
            if boss1_health <= 0:
                explosion = Explosion2(boss1_object.rect.center, explosion3_images)
                explosions.add(explosion)
                boss1_object.kill()
                score += 400

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        boss1_object.rect.centerx,
                        boss1_object.rect.centery,
                        double_refill_img,
                    )
                    double_refill_group.add(double_refill)

        for boss1_bullet in boss1_bullets:
            if boss1_bullet.rect.colliderect(player.rect):
                player_life -= 20
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                boss1_bullet.kill()

        if boss1_health <= 0:
            explosion = Explosion2(boss1_object.rect.center, explosion2_images)
            explosions2.add(explosion)
            boss1_object.kill()

    if boss1_group:
        boss1_object = boss1_group.sprites()[0]
        boss1_health_bar_rect.center = (boss1_object.rect.centerx, boss1_object.rect.top - 5)
        pygame.draw.rect(screen, (255, 0, 0), boss1_health_bar_rect)
        pygame.draw.rect(screen, (0, 255, 0), (boss1_health_bar_rect.left, boss1_health_bar_rect.top, boss1_health, boss1_health_bar_rect.height))

    for boss2_object in boss2_group:
        boss2_object.update(boss2_bullets, player)
        boss2_group.draw(screen)
        boss2_bullets.update()
        boss2_bullets.draw(screen)

        if boss2_object.rect.colliderect(player.rect):
            player_life -= 2
            explosion2 = Explosion2(boss2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)

        bullet_collisions = pygame.sprite.spritecollide(boss2_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion2(boss2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            boss2_health -= 8
            if boss2_health <= 0:
                explosion2 = Explosion2(boss2_object.rect.center, explosion3_images)
                explosions2.add(explosion2)
                boss2_object.kill()
                score += 800

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        boss2_object.rect.centerx,
                        boss2_object.rect.centery,
                        double_refill_img,
                    )
                    double_refill_group.add(double_refill)

        for boss2_bullet in boss2_bullets:
            if boss2_bullet.rect.colliderect(player.rect):
                player_life -= 20
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                boss2_bullet.kill()

        if boss2_health <= 0:
            explosion = Explosion2(boss2_object.rect.center, explosion2_images)
            explosions2.add(explosion)
            boss2_object.kill()

    if boss2_group:
        boss2_object = boss2_group.sprites()[0]
        boss2_health_bar_rect.center = (boss2_object.rect.centerx, boss2_object.rect.top - 5)
        pygame.draw.rect(screen, (255, 0, 0), boss2_health_bar_rect)
        pygame.draw.rect(screen, (0, 255, 0), (boss2_health_bar_rect.left, boss2_health_bar_rect.top, boss2_health, boss2_health_bar_rect.height))

    for boss3_object in boss3_group:
        boss3_object.update(boss3_bullets, player)
        boss3_group.draw(screen)
        boss3_bullets.update()
        boss3_bullets.draw(screen)

        if boss3_object.rect.colliderect(player.rect):
            player_life -= 1
            explosion2 = Explosion2(boss3_object.rect.center, explosion2_images)
            explosions2.add(explosion2)

        bullet_collisions = pygame.sprite.spritecollide(boss3_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion2(boss3_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            boss3_health -= 6
            if boss3_health <= 0:
                explosion2 = Explosion2(boss3_object.rect.center, explosion3_images)
                explosions2.add(explosion2)
                boss3_object.kill()
                score += 1000

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        boss3_object.rect.centerx,
                        boss3_object.rect.centery,
                        double_refill_img,
                    )
                    double_refill_group.add(double_refill)

        for boss3_bullet in boss3_bullets:
            if boss3_bullet.rect.colliderect(player.rect):
                player_life -= 20
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                boss3_bullet.kill()

        if boss3_health <= 0:
            explosion = Explosion2(boss3_object.rect.center, explosion2_images)
            explosions2.add(explosion)
            boss3_object.kill()
            get_name()
            show_game_win(screen)
            save_score(name, score)

            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()

    if boss3_group:
        boss3_object = boss3_group.sprites()[0]
        boss3_health_bar_rect.center = (boss3_object.rect.centerx, boss3_object.rect.top - 5)
        pygame.draw.rect(screen, (255, 0, 0), boss3_health_bar_rect)
        pygame.draw.rect(screen, (0, 255, 0), (boss3_health_bar_rect.left, boss3_health_bar_rect.top, boss3_health, boss3_health_bar_rect.height))

    player_image_copy = player.image.copy()
    screen.blit(player_image_copy, player.rect)

    for explosion in explosions:
        explosion.update()
        screen.blit(explosion.image, explosion.rect)

    for explosion2 in explosions2:
        explosion2.update()
        screen.blit(explosion2.image, explosion2.rect)

    for bullet in bullets:
        bullet.update()
        screen.blit(bullet.image, bullet.rect)

        if bullet.rect.bottom < 0:
            bullet.kill()
            bullet_counter -= 1

    player_life_surface = pygame.Surface((200, 25), pygame.SRCALPHA, 32)
    player_life_surface.set_alpha(216)

    player_life_bar_width = int(player_life / 200 * 200)
    player_life_bar_width = max(0, min(player_life_bar_width, 200))

    player_life_bar = pygame.Surface((player_life_bar_width, 30), pygame.SRCALPHA, 32)
    player_life_bar.set_alpha(216)

    life_bar_image = pygame.image.load("Pygame/images/life_bar.png").convert_alpha()

    if player_life > 50:
        player_life_bar.fill((152, 251, 152))
    else:
        player_life_bar.fill((0, 0, 0))

    #Se actualizan y dibujan los elementos del juego, como el jugador, las balas, los enemigos, las explosiones y las barras de vida y munición.
    player_life_surface.blit(life_bar_image, (0, 0))
    player_life_surface.blit(player_life_bar, (35, 0))

    life_x_pos = 10
    screen.blit(player_life_surface, (life_x_pos, 10))

    bullet_counter_surface = pygame.Surface((200, 25), pygame.SRCALPHA, 32)
    bullet_counter_surface.set_alpha(216)
    bullet_counter_bar = pygame.Surface(((bullet_counter / 200) * 200, 30), pygame.SRCALPHA, 32)
    bullet_counter_bar.set_alpha(216)
    bullet_bar_image = pygame.image.load("Pygame/images/bullet_bar.png").convert_alpha()
    if bullet_counter > 50:
        bullet_counter_bar.fill((255, 23, 23))
    else:
        bullet_counter_bar.fill((0, 0, 0))
    bullet_counter_surface.blit(bullet_bar_image, (0, 0))
    bullet_counter_surface.blit(bullet_counter_bar, (35, 0))
    bullet_x_pos = 10
    bullet_y_pos = player_life_surface.get_height() + 20
    screen.blit(bullet_counter_surface, (bullet_x_pos, bullet_y_pos))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'fonts', 'PublicPixel.ttf')
    font_name = font_path

    #Se muestra la puntuación actual, la puntuación más alta y el nombre del jugador en la pantalla.
    score_surface = pygame.font.SysFont(font_name, 30).render(f'SCORE: {score}', True, (255, 255, 255))
    score_surface.set_alpha(128)
    score_x_pos = (screen.get_width() - score_surface.get_width()) // 2
    score_image_rect = score_surface.get_rect()
    score_image_rect.x, score_image_rect.y = WIDTH - score_image_rect.width - extra_score_img.get_width() - 10, 10
    screen.blit(extra_score_img, (score_image_rect.right + 5, score_image_rect.centery - extra_score_img.get_height()//2))
    screen.blit(score_surface, score_image_rect)

    hi_score_surface = pygame.font.SysFont(font_name, 30).render(f'HIGH SCORE: {hi_score}', True, (255, 255, 255))
    hi_score_surface.set_alpha(128)
    hi_score_x_pos = (screen.get_width() - hi_score_surface.get_width()) // 2
    hi_score_y_pos = 2
    screen.blit(hi_score_surface, (hi_score_x_pos, hi_score_y_pos))

    name_surface = pygame.font.SysFont(font_name, 30).render(f'NOMBRE: {name}', True, (255, 255, 255))
    name_surface.set_alpha(128)
    name_x_pos = (screen.get_width() - name_surface.get_width()) // 2
    name_y_pos = 24
    screen.blit(name_surface, (name_x_pos, name_y_pos))

    pygame.display.flip()

    clock.tick(FPS)

pygame.mixer.music.stop()
pygame.quit()
sys.exit()
