from django.db import models


class Home(models.Model):
    name = models.TextField(verbose_name="Название")
    address = models.TextField(null=True, verbose_name="Адрес")
    
    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"
    
    def __str__(self):
        return f'Дом "{self.name}"'

class Entity(models.Model):
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    controller_id = models.IntegerField(verbose_name="Контроллер")
    light = models.BooleanField(default=False, verbose_name="Свет")
    tv = models.BooleanField(default=False, verbose_name="Телевизор")
    kettle = models.BooleanField(default=False, verbose_name="Чайник")
    vacuum_cleaner = models.BooleanField(default=False, verbose_name="Пылесос")
    
    class Meta:
        verbose_name = "Подключённые устройства"
        verbose_name_plural = "Подключённые устройства"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'Устройства, подключённые к дому "{self.home.name}"'

class Status(models.Model):
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    light = models.TextField(default="off", verbose_name="Свет")
    tv = models.TextField(default="off", verbose_name="Телевизор")
    kettle = models.TextField(default="0", verbose_name="Чайник")
    vacuum_cleaner = models.TextField(default="off", verbose_name="Пылесос")
    
    class Meta:
        verbose_name = "Статус устройств"
        verbose_name_plural = "Статусы устройств"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'Статус устройств, подключённых к дому "{self.home.name}"'

class Actions(models.Model):
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    entity = models.TextField(verbose_name="Устройство")
    switching = models.BooleanField(default=True, verbose_name="Переключение")
    volume = models.BooleanField(default=False, verbose_name="Громкость")
    brightness = models.BooleanField(default=False, verbose_name="Яркость")
    color = models.BooleanField(default=False, verbose_name="Цвет")
    temperature = models.BooleanField(default=False, verbose_name="Температура")
    
    class Meta:
        verbose_name = "Матрица возможностей"
        verbose_name_plural = "Матрицы возможностей"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'Матрица возможностей устройства "{self.entity}" в доме "{self.home.name}"'

class Settings(models.Model):
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, default="ru", verbose_name="Язык") # по стандартам ISO языки кодируются в 2-3 буквы
    auto_off = models.BooleanField(default=False, verbose_name="Авто выключение")
    night_mode = models.BooleanField(default=False, verbose_name="Ночной режим")
    
    class Meta:
        verbose_name = "Настройки дома"
        verbose_name_plural = "Настройки домов"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'Настройки дома "{self.home.name}"'

class Router(models.Model):
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Имя")
    ip_address = models.CharField(max_length=15, verbose_name="IP-адрес") # по длине адреса ipv4
    wifi_enabled = models.BooleanField(default=True, verbose_name="Доступен в сети")
    
    class Meta:
        verbose_name = "Роутер"
        verbose_name_plural = "Роутеры"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'Роутер "{self.name}" дома "{self.home.name}"'

class Controller(models.Model):
    controller_choices = [
        ("online", "онлайн"),
        ("offline", "оффлайн")
    ]
    
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Имя")
    ip_address = models.CharField(max_length=15, verbose_name="IP-адрес")
    status = models.CharField(max_length=7, choices=controller_choices, verbose_name="Статус")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Последний раз в сети")
        
    class Meta:
        verbose_name = "Контроллер"
        verbose_name_plural = "Контроллеры"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'Контроллер "{self.name}" дома "{self.home.name}"'

class WiFi(models.Model):
    home = models.ForeignKey(Home, verbose_name="Дом", on_delete=models.CASCADE)
    ssid = models.CharField(verbose_name="SSID")
    password = models.CharField(verbose_name="Пароль")
    hidden = models.BooleanField(default=False, verbose_name="Скрыта")
    
    class Meta:
        verbose_name = "WiFi-сеть"
        verbose_name_plural = "WiFi-сети"
        ordering = ["home__id"]
        
    def __str__(self):
        return f'WiFi-сеть дома "{self.home.name}"'

