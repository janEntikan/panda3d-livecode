# Welcome to panda3d-livecode.

# Ctrl-tab to (un)hide
# Ctrl-n for new
# Ctrl-o to open
# Ctrl-s to save
# Ctrl-q to quit
# Enter or shift-enter to refresh game.
# Drag mouse to move camera.


class Game():
    def __init__(self):
        self.models = {
            'player' : loader.load_model('example/ship.bam'),
            'monster' : loader.load_model('example/monster.bam'),
            'bullet' : loader.load_model('example/bullet.bam'),
        }

        self.player = self.spawn('player')
        self.bullets = []
        self.enemies = []
        self.spawn_enemies()

        self.cooldown = [0.2,0.2]
        self.bullet_speed = 20
        self.player_speed = 10

        base.cam.set_pos(0,-40, 20)
        base.cam.look_at((0,20,0))
        base.task_mgr.add(self.update)

    def spawn(self, model='player'):
        return self.models[model].copy_to(render)

    def spawn_enemies(self):
        for i in range(10):
            self.enemies.append(self.spawn('monster'))
            self.enemies[i].set_x(-10+(i*2))
            self.enemies[i].set_y(40)

    def hit_enemy(self, bullet):
        for enemy in self.enemies:
            if bullet.get_distance(enemy) < 0.5:
                enemy.detach_node()
                self.enemies.remove(enemy)
                return True

    def update_player(self):
        dt = globalClock.get_dt()
        is_down = base.mouseWatcherNode.is_button_down
        if is_down('arrow_left'):
            self.player.set_x(self.player, -self.player_speed*dt)
        if is_down('arrow_right'):
            self.player.set_x(self.player, self.player_speed*dt)

    def update_bullets(self):
        dt = globalClock.get_dt()
        self.cooldown[0] -= dt
        if self.cooldown[0] < 0:
            self.cooldown[0] = self.cooldown[1]
            bullet = self.spawn('bullet')
            bullet.set_pos(self.player.get_pos())
            self.bullets.append(bullet)

        for bullet in self.bullets:
            bullet.set_y(bullet, self.bullet_speed*dt)
            if bullet.get_y() > 60 or self.hit_enemy(bullet):
                bullet.detach_node()
                self.bullets.remove(bullet)

    def update(self, task):
        self.update_player()
        self.update_bullets()
        if len(self.enemies) == 0:
            self.spawn_enemies()
        return task.cont

game = Game()
