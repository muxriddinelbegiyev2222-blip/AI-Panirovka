# ... faylning yuqori qismi (importlar) o'zgarishsiz qoladi ...

# =============================================================================
# 1. YANGI TASODIFIY GENOM YARATISH (INITIALIZATION)
# =============================================================================

def create_random_floor_genome(
    requests: List[RoomRequest], 
    floor_index: int, 
    rng: random.Random
) -> FloorGenome:
    genome = FloorGenome(floor_index=floor_index)
    
    for req in requests:
        spec = get_room_spec(req.room_type)
        
        if req.room_type == "xoll":
            genome.wing_assignment[req.id] = "center"
            continue
            
        choices = ["left", "right", "top"]
        weights = [0.4, 0.4, 0.2]
        
        if spec.category in ("public", "wet"):
            weights = [0.45, 0.45, 0.1]
        elif spec.category == "private":
            weights = [0.35, 0.35, 0.3]
            
        wing = rng.choices(choices, weights=weights, k=1)[0]
        genome.wing_assignment[req.id] = wing
        genome.rotations[req.id] = rng.choice([True, False])

    # Xonalarni tartibga solish (shuffle)
    ids = list(genome.wing_assignment.keys())
    for room_id in ids:
        wing = genome.wing_assignment[room_id]
        if wing == "left":
            genome.left_order.append(room_id)
        elif wing == "right":
            genome.right_order.append(room_id)
        elif wing == "top":
            genome.top_order.append(room_id)
            
    rng.shuffle(genome.left_order)
    rng.shuffle(genome.right_order)
    rng.shuffle(genome.top_order)
    
    genome.hall_w = rng.uniform(MIN_HALL_WIDTH, MAX_HALL_WIDTH)
    genome.hall_h_ratio = rng.uniform(MIN_HALL_HEIGHT_RATIO, MAX_HALL_HEIGHT_RATIO)
    
    return genome

# ... create_random_house_genome o'zgarishsiz qoladi ...

# =============================================================================
# 2. MUTATSIYA (NASLNING O'ZGARISHI)
# =============================================================================

def mutate_floor_genome(
    genome: FloorGenome, 
    requests: List[RoomRequest], 
    rng: random.Random, 
    mutation_rate: float
) -> FloorGenome:
    new_genome = genome.copy()
    
    if rng.random() > mutation_rate:
        return new_genome

    mutation_type = rng.choice([
        "swap_order", "change_wing", "toggle_rotation", "change_hall"
    ])

    if mutation_type == "swap_order":
        lists = [new_genome.left_order, new_genome.right_order, new_genome.top_order]
        valid_lists = [l for l in lists if len(l) > 1]
        if valid_lists:
            target_list = rng.choice(valid_lists)
            i, j = rng.sample(range(len(target_list)), 2)
            target_list[i], target_list[j] = target_list[j], target_list[i]

    elif mutation_type == "change_wing":
        all_rooms = new_genome.all_room_ids()
        if all_rooms:
            room_id = rng.choice(all_rooms)
            
            # Xollni ko'chirib bo'lmaydi
            req = next((r for r in requests if r.id == room_id), None)
            if req and req.room_type == "xoll":
                return new_genome
            
            old_wing = new_genome.wing_assignment.get(room_id, "left")
            new_wing = rng.choice(["left", "right", "top"])
            
            if old_wing != new_wing:
                # Xavfsiz o'chirish (agar ro'yxatda bo'lsa)
                if old_wing == "left" and room_id in new_genome.left_order: new_genome.left_order.remove(room_id)
                elif old_wing == "right" and room_id in new_genome.right_order: new_genome.right_order.remove(room_id)
                elif old_wing == "top" and room_id in new_genome.top_order: new_genome.top_order.remove(room_id)
                
                new_genome.wing_assignment[room_id] = new_wing
                if new_wing == "left": new_genome.left_order.insert(rng.randint(0, len(new_genome.left_order)), room_id)
                elif new_wing == "right": new_genome.right_order.insert(rng.randint(0, len(new_genome.right_order)), room_id)
                elif new_wing == "top": new_genome.top_order.insert(rng.randint(0, len(new_genome.top_order)), room_id)

    elif mutation_type == "toggle_rotation":
        all_rooms = new_genome.all_room_ids()
        if all_rooms:
            room_id = rng.choice(all_rooms)
            new_genome.rotations[room_id] = not new_genome.rotations.get(room_id, False)

    elif mutation_type == "change_hall":
        if rng.random() < 0.5:
            new_genome.hall_w = max(MIN_HALL_WIDTH, min(MAX_HALL_WIDTH, new_genome.hall_w + rng.uniform(-0.5, 0.5)))
        else:
            new_genome.hall_h_ratio = max(MIN_HALL_HEIGHT_RATIO, min(MAX_HALL_HEIGHT_RATIO, new_genome.hall_h_ratio + rng.uniform(-0.05, 0.05)))

    return new_genome


# =============================================================================
# 3. KROSSOVER (OTA-ONA GENLARINI BIRLASHTIRISH)
# =============================================================================

def crossover_house_genomes(
    parent1: HouseGenome, 
    parent2: HouseGenome, 
    rng: random.Random
) -> Tuple[HouseGenome, HouseGenome]:
    child1 = HouseGenome()
    child2 = HouseGenome()
    
    for f_idx in range(min(parent1.story_count(), parent2.story_count())):
        p1 = parent1.floor_genomes[f_idx]
        p2 = parent2.floor_genomes[f_idx]
        
        c1 = p1.copy()
        c2 = p2.copy()
        
        if rng.random() < 0.5:
            c1.hall_w = p2.hall_w
            c2.hall_w = p1.hall_w
            
        if rng.random() < 0.7:
            c1.left_order = list(p1.left_order) + [r for r in p2.left_order if r not in p1.left_order]
            c2.left_order = list(p2.left_order) + [r for r in p1.left_order if r not in p2.left_order]
            c1.right_order = list(p1.right_order) + [r for r in p2.right_order if r not in p1.right_order]
            c2.right_order = list(p2.right_order) + [r for r in p1.right_order if r not in p2.right_order]
            
        # Wing assignment ni noldan xavfsiz qurish
        c1.wing_assignment = {}
        for rid in c1.left_order: c1.wing_assignment[rid] = "left"
        for rid in c1.right_order: c1.wing_assignment[rid] = "right"
        for rid in c1.top_order: c1.wing_assignment[rid] = "top"
        
        c2.wing_assignment = {}
        for rid in c2.left_order: c2.wing_assignment[rid] = "left"
        for rid in c2.right_order: c2.wing_assignment[rid] = "right"
        for rid in c2.top_order: c2.wing_assignment[rid] = "top"

        child1.floor_genomes.append(c1)
        child2.floor_genomes.append(c2)
        
    child1.staircase_slot = rng.choice([parent1.staircase_slot, parent2.staircase_slot])
    child2.staircase_slot = rng.choice([parent1.staircase_slot, parent2.staircase_slot])
    
    return child1, child2
