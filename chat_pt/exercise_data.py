"""
Exercise library seed data with YouTube video demonstrations.
YouTube links are from reputable fitness channels for proper form demonstration.
"""

EXERCISE_LIBRARY = [
    # ==================== UPPER BODY ====================

    # CHEST EXERCISES
    {
        "name": "Barbell Bench Press",
        "category": "Upper Body",
        "primary_muscles": "Pectoralis Major, Triceps",
        "secondary_muscles": "Anterior Deltoids",
        "equipment": "Barbell, Bench",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=rT7DgCr-3pg",
        "instructions": "1. Lie on bench with eyes under bar\n2. Grip bar slightly wider than shoulder-width\n3. Unrack and lower bar to mid-chest\n4. Press bar up in slight arc to starting position\n5. Keep feet flat on floor, maintain arch",
        "form_cues": "• Retract shoulder blades\n• Keep elbows at 45° angle\n• Touch chest lightly, don't bounce\n• Drive through legs for stability"
    },
    {
        "name": "Dumbbell Bench Press",
        "category": "Chest",
        "primary_muscles": "Pectoralis Major, Triceps",
        "secondary_muscles": "Anterior Deltoids, Stabilizers",
        "equipment": "Dumbbells, Bench",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=VmB1G1K7v94",
        "instructions": "1. Sit on edge of bench with dumbbells on thighs\n2. Lie back and bring dumbbells to chest level\n3. Press dumbbells up until arms extended\n4. Lower with control to starting position\n5. Maintain natural arch in lower back",
        "form_cues": "• Keep wrists straight\n• Lower until slight stretch in chest\n• Press in slight arc, bringing dumbbells together\n• Control the descent"
    },
    {
        "name": "Push-Ups",
        "category": "Chest",
        "primary_muscles": "Pectoralis Major, Triceps",
        "secondary_muscles": "Anterior Deltoids, Core",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "instructions": "1. Start in plank position, hands shoulder-width\n2. Lower body until chest nearly touches floor\n3. Push back up to starting position\n4. Keep body in straight line throughout\n5. Breathe in on descent, out on ascent",
        "form_cues": "• Keep core tight\n• Don't let hips sag\n• Elbows at 45° angle\n• Full range of motion"
    },

    # BACK EXERCISES
    {
        "name": "Barbell Row",
        "category": "Back",
        "primary_muscles": "Latissimus Dorsi, Rhomboids",
        "secondary_muscles": "Biceps, Lower Back",
        "equipment": "Barbell",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=FWJR5Ve8bnQ",
        "instructions": "1. Stand with feet hip-width, barbell over mid-foot\n2. Hinge at hips, grip bar shoulder-width\n3. Pull bar to lower chest/upper abdomen\n4. Lower with control to starting position\n5. Keep back flat throughout movement",
        "form_cues": "• Lead with elbows\n• Squeeze shoulder blades together\n• Don't use momentum\n• Maintain neutral spine"
    },
    {
        "name": "Pull-Ups",
        "category": "Back",
        "primary_muscles": "Latissimus Dorsi, Biceps",
        "secondary_muscles": "Rhomboids, Rear Deltoids",
        "equipment": "Pull-up Bar",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g",
        "instructions": "1. Hang from bar with overhand grip, hands shoulder-width\n2. Pull yourself up until chin over bar\n3. Lower with control to full hang\n4. Keep core engaged throughout\n5. Avoid swinging or kipping",
        "form_cues": "• Full range of motion\n• Pull elbows down and back\n• Chest to bar if possible\n• Controlled descent"
    },
    {
        "name": "Lat Pulldown",
        "category": "Back",
        "primary_muscles": "Latissimus Dorsi",
        "secondary_muscles": "Biceps, Rear Deltoids",
        "equipment": "Cable Machine",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
        "instructions": "1. Sit at machine, adjust thigh pad\n2. Grip bar wider than shoulder-width\n3. Pull bar down to upper chest\n4. Squeeze shoulder blades together\n5. Control return to starting position",
        "form_cues": "• Slight lean back\n• Pull elbows down and back\n• Don't use momentum\n• Full stretch at top"
    },
    {
        "name": "Deadlift",
        "category": "Back",
        "primary_muscles": "Erector Spinae, Glutes, Hamstrings",
        "secondary_muscles": "Lats, Traps, Forearms",
        "equipment": "Barbell",
        "difficulty": "Advanced",
        "youtube_url": "https://www.youtube.com/watch?v=op9kVnSso6Q",
        "instructions": "1. Stand with feet hip-width, bar over mid-foot\n2. Bend down and grip bar just outside legs\n3. Chest up, back flat, hips higher than knees\n4. Drive through floor, stand up fully\n5. Lower bar with control, maintaining form",
        "form_cues": "• Neutral spine throughout\n• Drive through heels\n• Bar stays close to body\n• Hips and shoulders rise together"
    },

    # SHOULDER EXERCISES
    {
        "name": "Overhead Press",
        "category": "Shoulders",
        "primary_muscles": "Deltoids, Triceps",
        "secondary_muscles": "Upper Chest, Core",
        "equipment": "Barbell",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=2yjwXTZQDDI",
        "instructions": "1. Stand with feet shoulder-width, bar at shoulders\n2. Grip bar just outside shoulders\n3. Press bar straight up overhead\n4. Lock out arms at top\n5. Lower with control to starting position",
        "form_cues": "• Keep core tight\n• Don't arch back excessively\n• Bar path slightly back over head\n• Full lockout at top"
    },
    {
        "name": "Lateral Raise",
        "category": "Shoulders",
        "primary_muscles": "Lateral Deltoids",
        "secondary_muscles": "Anterior Deltoids, Traps",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=3VcKaXpzqRo",
        "instructions": "1. Stand with dumbbells at sides, slight bend in elbows\n2. Raise arms out to sides until shoulder height\n3. Pause briefly at top\n4. Lower with control to starting position\n5. Maintain slight forward lean",
        "form_cues": "• Lead with elbows\n• Don't swing weights\n• Slight bend in elbows\n• Control the negative"
    },

    # LEG EXERCISES
    {
        "name": "Barbell Back Squat",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes, Hamstrings",
        "secondary_muscles": "Core, Erectors",
        "equipment": "Barbell, Squat Rack",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=ultWZbUMPL8",
        "instructions": "1. Bar on upper back, feet shoulder-width\n2. Unrack and step back\n3. Descend by breaking at hips and knees\n4. Lower until thighs parallel or below\n5. Drive through heels to stand",
        "form_cues": "• Chest up, core braced\n• Knees track over toes\n• Full depth if mobility allows\n• Drive knees out"
    },
    {
        "name": "Romanian Deadlift",
        "category": "Legs",
        "primary_muscles": "Hamstrings, Glutes",
        "secondary_muscles": "Lower Back, Lats",
        "equipment": "Barbell",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=2SHsk9AzdjA",
        "instructions": "1. Stand with barbell at hip height\n2. Slight knee bend, push hips back\n3. Lower bar down shins, feel hamstring stretch\n4. Stop when back starts to round\n5. Drive hips forward to return",
        "form_cues": "• Keep bar close to legs\n• Neutral spine\n• Push hips back, not down\n• Feel stretch in hamstrings"
    },
    {
        "name": "Leg Press",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes",
        "secondary_muscles": "Hamstrings",
        "equipment": "Leg Press Machine",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=IZxyjW7MPJQ",
        "instructions": "1. Sit in machine, feet shoulder-width on platform\n2. Release safety, lower platform with control\n3. Lower until knees at 90° or slightly below\n4. Press through heels to extend legs\n5. Don't lock knees at top",
        "form_cues": "• Keep lower back pressed to pad\n• Full range of motion\n• Don't bounce at bottom\n• Controlled tempo"
    },
    {
        "name": "Lunges",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes",
        "secondary_muscles": "Hamstrings, Core",
        "equipment": "Dumbbells (optional)",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=QOVaHwm-Q6U",
        "instructions": "1. Stand with feet hip-width apart\n2. Step forward with one leg\n3. Lower until both knees at 90°\n4. Push through front heel to return\n5. Alternate legs",
        "form_cues": "• Keep torso upright\n• Front knee over ankle\n• Back knee just above floor\n• Long stride"
    },

    # ARM EXERCISES
    {
        "name": "Barbell Curl",
        "category": "Arms",
        "primary_muscles": "Biceps",
        "secondary_muscles": "Forearms",
        "equipment": "Barbell",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=kwG2ipFRgfo",
        "instructions": "1. Stand with feet shoulder-width, bar in hands\n2. Curl bar up to shoulders\n3. Squeeze biceps at top\n4. Lower with control to starting position\n5. Keep elbows stationary",
        "form_cues": "• Don't swing body\n• Keep elbows tight to sides\n• Full range of motion\n• Controlled eccentric"
    },
    {
        "name": "Tricep Dips",
        "category": "Arms",
        "primary_muscles": "Triceps",
        "secondary_muscles": "Chest, Anterior Deltoids",
        "equipment": "Parallel Bars or Bench",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=2z8JmcrW-As",
        "instructions": "1. Grip bars or bench edge, support bodyweight\n2. Lower body by bending elbows\n3. Descend until upper arms parallel to ground\n4. Push back up to starting position\n5. Keep body upright for tricep focus",
        "form_cues": "• Don't shrug shoulders\n• Elbows back, not flared\n• Controlled descent\n• Full extension at top"
    },

    # CORE EXERCISES
    {
        "name": "Plank",
        "category": "Core",
        "primary_muscles": "Rectus Abdominis, Transverse Abdominis",
        "secondary_muscles": "Shoulders, Glutes",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
        "instructions": "1. Start in forearm plank position\n2. Body in straight line from head to heels\n3. Engage core, squeeze glutes\n4. Hold position for prescribed time\n5. Breathe normally",
        "form_cues": "• Don't let hips sag\n• Keep neck neutral\n• Squeeze everything\n• Quality over duration"
    },
    {
        "name": "Russian Twist",
        "category": "Core",
        "primary_muscles": "Obliques, Rectus Abdominis",
        "secondary_muscles": "Hip Flexors",
        "equipment": "Dumbbell or Plate (optional)",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=wkD8rjkodUI",
        "instructions": "1. Sit with knees bent, feet off floor\n2. Lean back slightly, core engaged\n3. Rotate torso side to side\n4. Touch weight/hands to floor each side\n5. Keep movement controlled",
        "form_cues": "• Rotate from core, not arms\n• Keep chest up\n• Controlled rotation\n• Breathe throughout"
    },

    # ==================== RUGBY/FUNCTIONAL EXERCISES ====================

    # POWER & EXPLOSIVE MOVEMENTS
    {
        "name": "Power Clean",
        "category": "Legs",
        "primary_muscles": "Hamstrings, Glutes, Traps, Quads",
        "secondary_muscles": "Core, Shoulders, Upper Back",
        "equipment": "Barbell",
        "difficulty": "Advanced",
        "youtube_url": "https://www.youtube.com/watch?v=KwYJTpQ_x5A",
        "instructions": "1. Start in deadlift position, bar over mid-foot\n2. Explosively extend hips, knees, and ankles\n3. Shrug shoulders and pull bar up\n4. Drop under bar, catch at shoulders\n5. Stand to full extension",
        "form_cues": "• Triple extension (ankles, knees, hips)\n• Fast elbows\n• Catch with soft knees\n• Keep bar close to body"
    },
    {
        "name": "Box Jump",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes, Calves",
        "secondary_muscles": "Core, Hip Flexors",
        "equipment": "Plyo Box",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=52r_Ul5k03g",
        "instructions": "1. Stand facing box, feet hip-width\n2. Swing arms back, quarter squat\n3. Explosively jump onto box\n4. Land softly with bent knees\n5. Step down (don't jump down)",
        "form_cues": "• Soft landing\n• Full hip extension at top\n• Reset between reps\n• Quality over quantity"
    },
    {
        "name": "Broad Jump",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes, Hamstrings",
        "secondary_muscles": "Calves, Core",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=LFl6Ar3fZ4g",
        "instructions": "1. Start with feet hip-width\n2. Swing arms back, load hips\n3. Jump forward explosively\n4. Land in athletic position\n5. Measure distance for progress tracking",
        "form_cues": "• Drive arms forward\n• Push through ground\n• Land balanced\n• Absorb landing with legs"
    },
    {
        "name": "Medicine Ball Slam",
        "category": "Core",
        "primary_muscles": "Core, Lats, Shoulders",
        "secondary_muscles": "Entire Body",
        "equipment": "Medicine Ball",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=LFUHJQZYRjk",
        "instructions": "1. Hold medicine ball overhead\n2. Rise onto toes, extend fully\n3. Slam ball down with maximum force\n4. Catch on bounce or pick up\n5. Repeat explosively",
        "form_cues": "• Full body engagement\n• Explosive power\n• Use core, not just arms\n• Keep back safe"
    },

    # STRENGTH & CONTACT PREPARATION
    {
        "name": "Front Squat",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes",
        "secondary_muscles": "Core, Upper Back",
        "equipment": "Barbell",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=uYumuL_G_V0",
        "instructions": "1. Bar rests on front delts, elbows high\n2. Feet shoulder-width, toes slightly out\n3. Descend keeping chest up\n4. Lower until thighs parallel\n5. Drive through heels to stand",
        "form_cues": "• Elbows stay high\n• Chest up throughout\n• Core braced hard\n• More upright than back squat"
    },
    {
        "name": "Farmer's Walk",
        "category": "Back",
        "primary_muscles": "Traps, Forearms, Core",
        "secondary_muscles": "Entire Body",
        "equipment": "Dumbbells or Trap Bar",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=rt17lmztSlY",
        "instructions": "1. Pick up heavy dumbbells/weights\n2. Stand tall with weights at sides\n3. Walk forward with controlled steps\n4. Keep shoulders back and down\n5. Walk prescribed distance",
        "form_cues": "• Tight core\n• Don't let shoulders shrug up\n• Controlled breathing\n• Strong grip"
    },
    {
        "name": "Sled Push",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes, Calves",
        "secondary_muscles": "Core, Shoulders, Chest",
        "equipment": "Weighted Sled",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=PJeIeVKC9NY",
        "instructions": "1. Hands on sled, arms extended\n2. Lean forward at 45° angle\n3. Drive legs powerfully\n4. Short, powerful steps\n5. Push for prescribed distance",
        "form_cues": "• Stay low\n• Drive through ground\n• Straight line from head to heel\n• Explosive leg drive"
    },
    {
        "name": "Sled Drag/Pull",
        "category": "Legs",
        "primary_muscles": "Hamstrings, Glutes, Upper Back",
        "secondary_muscles": "Core, Lats",
        "equipment": "Weighted Sled with Rope",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=qv7kmv8zVi4",
        "instructions": "1. Attach rope to sled\n2. Walk backward pulling sled\n3. Lean back slightly\n4. Use upper back and arms to pull\n5. Powerful backward strides",
        "form_cues": "• Pull with lats\n• Stay balanced\n• Short powerful steps\n• Core engaged"
    },

    # UPPER BODY POWER & CONTACT
    {
        "name": "Incline Bench Press",
        "category": "Chest",
        "primary_muscles": "Upper Chest, Triceps",
        "secondary_muscles": "Anterior Deltoids",
        "equipment": "Barbell, Incline Bench",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=jPLdzuHckI8",
        "instructions": "1. Set bench to 30-45° incline\n2. Lie back, feet flat on floor\n3. Lower bar to upper chest\n4. Press up to arms extended\n5. Control the descent",
        "form_cues": "• Don't bounce\n• Retract shoulder blades\n• Drive through bench\n• Full range of motion"
    },
    {
        "name": "Floor Press",
        "category": "Chest",
        "primary_muscles": "Chest, Triceps",
        "secondary_muscles": "Shoulders",
        "equipment": "Barbell or Dumbbells",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=LbzcEXs9Jt4",
        "instructions": "1. Lie on floor with bar at chest height\n2. Lower bar until elbows touch floor\n3. Pause briefly\n4. Press up explosively\n5. Great for lockout strength",
        "form_cues": "• Pause on floor\n• Don't relax at bottom\n• Explosive concentric\n• Good for rugby contact prep"
    },
    {
        "name": "Face Pulls",
        "category": "Back",
        "primary_muscles": "Rear Deltoids, Upper Back",
        "secondary_muscles": "Rotator Cuff",
        "equipment": "Cable Machine with Rope",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=rep-qVOkqgk",
        "instructions": "1. Set cable at face height\n2. Pull rope toward face\n3. Separate rope at end, hands past ears\n4. Squeeze shoulder blades\n5. Control return to start",
        "form_cues": "• Pull to face, not chest\n• External rotation at end\n• Shoulders back and down\n• Essential for shoulder health"
    },

    # CORE & STABILITY FOR CONTACT
    {
        "name": "Turkish Get-Up",
        "category": "Core",
        "primary_muscles": "Core, Shoulders, Full Body",
        "secondary_muscles": "Hip Stability, Balance",
        "equipment": "Kettlebell or Dumbbell",
        "difficulty": "Advanced",
        "youtube_url": "https://www.youtube.com/watch?v=0bWRPC49-KI",
        "instructions": "1. Lie on back, press weight overhead\n2. Roll to elbow, then hand\n3. Bridge hips up\n4. Sweep leg through\n5. Stand up, reverse to descend",
        "form_cues": "• Keep eyes on weight\n• Slow controlled movement\n• Excellent functional strength\n• Master technique first"
    },
    {
        "name": "Pallof Press",
        "category": "Core",
        "primary_muscles": "Obliques, Core Stability",
        "secondary_muscles": "Shoulders",
        "equipment": "Cable Machine or Band",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=AH_QZLm_0-s",
        "instructions": "1. Stand perpendicular to cable\n2. Hold handle at chest\n3. Press arms straight out\n4. Hold and resist rotation\n5. Return to chest",
        "form_cues": "• Don't rotate torso\n• Brace core hard\n• Slow controlled press\n• Anti-rotation strength"
    },
    {
        "name": "Dead Bug",
        "category": "Core",
        "primary_muscles": "Core, Hip Flexors",
        "secondary_muscles": "Shoulders",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=g_BYB0R-4Ws",
        "instructions": "1. Lie on back, arms up, knees bent\n2. Lower opposite arm and leg\n3. Keep lower back pressed to floor\n4. Return to start\n5. Alternate sides",
        "form_cues": "• No lower back arch\n• Slow controlled movement\n• Breathe throughout\n• Core stability fundamental"
    },

    # POSTERIOR CHAIN & INJURY PREVENTION
    {
        "name": "Nordic Hamstring Curl",
        "category": "Legs",
        "primary_muscles": "Hamstrings",
        "secondary_muscles": "Glutes, Calves",
        "equipment": "Partner or Anchor",
        "difficulty": "Advanced",
        "youtube_url": "https://www.youtube.com/watch?v=EthJV19wO6o",
        "instructions": "1. Kneel with ankles secured\n2. Keep body straight from knees to head\n3. Lower forward as slowly as possible\n4. Catch yourself with hands\n5. Push back up to start",
        "form_cues": "• Eccentric focus\n• Hamstring injury prevention\n• Use assistance if needed\n• Build up gradually"
    },
    {
        "name": "Bulgarian Split Squat",
        "category": "Legs",
        "primary_muscles": "Quadriceps, Glutes",
        "secondary_muscles": "Hamstrings, Core",
        "equipment": "Bench, Dumbbells (optional)",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=2C-uNgKwPLE",
        "instructions": "1. Back foot elevated on bench\n2. Front foot forward in lunge position\n3. Lower until front thigh parallel\n4. Drive through front heel to stand\n5. Keep torso upright",
        "form_cues": "• Front knee tracks over toe\n• Torso upright\n• Balance and stability\n• Single leg strength"
    },
    {
        "name": "Glute Bridge",
        "category": "Legs",
        "primary_muscles": "Glutes, Hamstrings",
        "secondary_muscles": "Core, Lower Back",
        "equipment": "Bodyweight or Barbell",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=wPM8icPu6H8",
        "instructions": "1. Lie on back, knees bent, feet flat\n2. Drive through heels\n3. Raise hips until body straight\n4. Squeeze glutes at top\n5. Lower with control",
        "form_cues": "• Squeeze glutes, not lower back\n• Full hip extension\n• Shoulders stay on ground\n• Posterior chain activation"
    },

    # UPPER BODY PULLING & GRIP
    {
        "name": "Chin-Ups",
        "category": "Back",
        "primary_muscles": "Lats, Biceps",
        "secondary_muscles": "Core, Forearms",
        "equipment": "Pull-up Bar",
        "difficulty": "Intermediate",
        "youtube_url": "https://www.youtube.com/watch?v=brhYEi8Nzv4",
        "instructions": "1. Hang from bar, underhand grip\n2. Pull chin over bar\n3. Lead with chest\n4. Lower with control\n5. Full range of motion",
        "form_cues": "• Underhand grip (supinated)\n• More bicep involvement\n• Full hang at bottom\n• Controlled tempo"
    },
    {
        "name": "Inverted Row",
        "category": "Back",
        "primary_muscles": "Upper Back, Lats",
        "secondary_muscles": "Biceps, Core",
        "equipment": "Barbell in Rack or TRX",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=hXTc1mDnZCw",
        "instructions": "1. Lie under bar, grab with overhand grip\n2. Keep body straight\n3. Pull chest to bar\n4. Squeeze shoulder blades\n5. Lower with control",
        "form_cues": "• Body stays rigid\n• Pull elbows back\n• Lower bar = harder\n• Great progression exercise"
    },

    # ADDITIONAL COMMON EXERCISES

    # CHEST ISOLATION
    {
        "name": "Cable Fly",
        "category": "Chest",
        "primary_muscles": "Pectoralis Major",
        "secondary_muscles": "Anterior Deltoids",
        "equipment": "Cable Machine",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=Iwe6AmxVf7o",
        "instructions": "1. Set cables to chest height\n2. Stand in center with slight forward lean\n3. Grab handles with arms extended\n4. Bring hands together in arc motion\n5. Squeeze chest, return with control",
        "form_cues": "• Maintain slight elbow bend\n• Think 'hugging a tree'\n• Control eccentric phase\n• Focus on chest squeeze"
    },

    # TRICEPS
    {
        "name": "Tricep Pushdown",
        "category": "Arms",
        "primary_muscles": "Triceps",
        "secondary_muscles": "None",
        "equipment": "Cable Machine, Rope or Bar",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=2-LAMcpzODU",
        "instructions": "1. Attach rope or bar to high pulley\n2. Stand facing cable, elbows at sides\n3. Push down until arms fully extended\n4. Squeeze triceps at bottom\n5. Return with control",
        "form_cues": "• Keep elbows locked at sides\n• Don't lean forward\n• Full extension at bottom\n• Controlled tempo"
    },

    # LEGS - HAMSTRINGS
    {
        "name": "Hamstring Curl",
        "category": "Legs",
        "primary_muscles": "Hamstrings",
        "secondary_muscles": "Calves",
        "equipment": "Leg Curl Machine",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=1Tq3QdYUuHs",
        "instructions": "1. Adjust machine, lie face down\n2. Position ankles under pad\n3. Curl legs toward glutes\n4. Squeeze hamstrings at top\n5. Lower with control",
        "form_cues": "• Keep hips down\n• Full range of motion\n• Don't hyperextend knees\n• Control the negative"
    },

    # LEGS - QUADRICEPS
    {
        "name": "Leg Extension",
        "category": "Legs",
        "primary_muscles": "Quadriceps",
        "secondary_muscles": "None",
        "equipment": "Leg Extension Machine",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=YyvSfEjZruE",
        "instructions": "1. Sit in machine, adjust shin pad\n2. Position pad above ankles\n3. Extend legs until straight\n4. Squeeze quads at top\n5. Lower with control",
        "form_cues": "• Back against pad\n• Full extension (don't lock)\n• Control descent\n• Great for quad isolation"
    },

    # SHOULDERS
    {
        "name": "Dumbbell Shoulder Press",
        "category": "Shoulders",
        "primary_muscles": "Deltoids",
        "secondary_muscles": "Triceps, Upper Chest",
        "equipment": "Dumbbells, Bench",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=qEwKCR5JCog",
        "instructions": "1. Sit on bench with back support\n2. Hold dumbbells at shoulder height\n3. Press overhead until arms extended\n4. Lower with control to shoulders\n5. Keep core engaged",
        "form_cues": "• Press straight up\n• Don't arch back excessively\n• Elbows slightly forward\n• Controlled descent"
    },

    # BACK - DUMBBELL VARIATION
    {
        "name": "Bent Over Dumbbell Row",
        "category": "Back",
        "primary_muscles": "Lats, Upper Back",
        "secondary_muscles": "Biceps, Core",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "youtube_url": "https://www.youtube.com/watch?v=roCP6wCXPqo",
        "instructions": "1. Hinge at hips, slight knee bend\n2. Hold dumbbells with neutral grip\n3. Pull dumbbells to hips\n4. Squeeze shoulder blades\n5. Lower with control",
        "form_cues": "• Keep back flat\n• Pull elbows back, not up\n• Torso near parallel to floor\n• Don't round lower back"
    },
]
