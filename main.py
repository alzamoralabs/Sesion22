from datetime import datetime, timedelta
from enum import Enum

class RelationType(Enum):
    KNOWS = "knows"
    LIVES_WITH = "lives_with"
    DRIVES = "drives"
    OWNS = "owns"

class Person:
    def __init__(self, name, birth_date, twitter=None):
        self.name = name
        self.birth_date = birth_date
        self.twitter = twitter
        self.relationships = {}
        self.driving_history = []
        
    def get_age(self):
        today = datetime.now()
        return today.year - self.birth_date.year
    
    def add_relationship(self, person, rel_type, since=None):
        if rel_type not in self.relationships:
            self.relationships[rel_type] = []
        self.relationships[rel_type].append({
            'person': person,
            'since': since
        })
    
    def drive_car(self, car, destination, duration_hours=1):
        action = {
            'timestamp': datetime.now(),
            'car': car,
            'destination': destination,
            'duration': duration_hours
        }
        self.driving_history.append(action)
        print(f"🚗 {self.name} está conduciendo el {car.brand} {car.model} hacia {destination}")
        print(f"   Duración estimada: {duration_hours} hora(s)")
        return action
    
    def __str__(self):
        return f"{self.name} (Nacido: {self.birth_date.strftime('%d-%m-%Y')}, Edad: {self.get_age()})"

class Car:
    def __init__(self, brand, model, description, embedding=None, wiki_source=None):
        self.brand = brand
        self.model = model
        self.description = description
        self.embedding = embedding
        self.wiki_source = wiki_source
        self.owner = None
        self.current_driver = None
        self.trip_history = []
    
    def set_owner(self, person):
        self.owner = person
        print(f"✓ {person.name} es ahora propietario del {self.brand} {self.model}")
    
    def register_trip(self, driver, destination, duration):
        trip = {
            'driver': driver.name,
            'destination': destination,
            'duration': duration,
            'timestamp': datetime.now(),
            'owner': self.owner.name if self.owner else None
        }
        self.trip_history.append(trip)
    
    def __str__(self):
        return f"{self.brand} {self.model}"

class Household:
    def __init__(self, members, shared_car=None):
        self.members = members
        self.shared_car = shared_car
        self.shared_tasks = []
    
    def schedule_driving(self, driver, destination, duration=1):
        if driver not in self.members:
            print(f"✗ {driver.name} no es miembro del hogar")
            return
        
        if self.shared_car:
            driver.drive_car(self.shared_car, destination, duration)
            self.shared_car.register_trip(driver, destination, duration)
        else:
            print(f"✗ No hay auto compartido disponible")
    
    def show_status(self):
        print(f"\n{'='*60}")
        print(f"ESTADO DEL HOGAR")
        print(f"{'='*60}")
        print(f"Miembros del hogar:")
        for member in self.members:
            print(f"  • {member}")
        
        if self.shared_car:
            print(f"\nAuto compartido: {self.shared_car}")
            print(f"Propietario: {self.shared_car.owner.name if self.shared_car.owner else 'Sin asignar'}")
            print(f"Viajes registrados: {len(self.shared_car.trip_history)}")
        
        print(f"{'='*60}\n")

# ============ SIMULACIÓN ============

# Crear personas
dan = Person("Dan", datetime(1970, 5, 29), "@dan")
ann = Person("Ann", datetime(1975, 12, 5))

# Crear auto
volvo = Car(
    brand="Volvo",
    model="V70",
    description="An executive car manufactured...",
    embedding=[0.1, -0.3, 0.4, -0.7],
    wiki_source="https://en.wikipedia.org/wiki/Volvo_V70"
)

# Establecer relaciones
dan.add_relationship(ann, RelationType.KNOWS)
ann.add_relationship(dan, RelationType.KNOWS)

dan.add_relationship(ann, RelationType.LIVES_WITH, datetime(2011, 1, 10))
ann.add_relationship(dan, RelationType.LIVES_WITH, datetime(2011, 1, 10))

# Asignar auto
volvo.set_owner(ann)

# Crear hogar compartido
hogar = Household([dan, ann], volvo)

# Mostrar estado inicial
print("\n" + "="*60)
print("SIMULACIÓN: DAN, ANN Y SU VOLVO V70")
print("="*60 + "\n")

hogar.show_status()

# Simular actividades de conducción
print("📋 REGISTRANDO ACTIVIDADES DE CONDUCCIÓN:\n")

hogar.schedule_driving(dan, "Trabajo", 0.5)
print()

hogar.schedule_driving(ann, "Centro comercial", 1.5)
print()

hogar.schedule_driving(dan, "Gimnasio", 0.75)
print()

# Mostrar historial
print("\n" + "="*60)
print("HISTORIAL DE VIAJES DEL VEHÍCULO")
print("="*60 + "\n")

for i, trip in enumerate(volvo.trip_history, 1):
    print(f"Viaje {i}:")
    print(f"  Conductor: {trip['driver']}")
    print(f"  Destino: {trip['destination']}")
    print(f"  Duración: {trip['duration']} hora(s)")
    print(f"  Propietario: {trip['owner']}")
    print()

# Mostrar información personal
print("="*60)
print("INFORMACIÓN PERSONAL")
print("="*60 + "\n")
print(dan)
print(f"  Twitter: {dan.twitter}")
print(f"  Viajes realizados: {len(dan.driving_history)}\n")

print(ann)
print(f"  Viajes realizados: {len(ann.driving_history)}\n")