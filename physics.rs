// physics.rs — Verlet-integrated 2D physics engine for Antigravity Claw

use rand::Rng;
use crate::types::*;

/// Gravity constant in different directions (px/s²)
const G: f64 = 980.0;

/// Step the entire world forward by dt seconds
pub fn step(world: &mut PhysicsWorld, dt: f64) {
    let ground = world.viewport_height;
    let ceil   = 0.0_f64;
    let left   = 0.0_f64;
    let right  = world.viewport_width;

    let (gx, gy) = gravity_vector(world.mode, world.gravity, world.tick);

    for elem in &mut world.elements {
        if elem.grounded && world.mode == GravityMode::Zero {
            continue;
        }

        // Apply gravity
        elem.velocity.x += gx * dt;
        elem.velocity.y += gy * dt;

        // Apply air resistance (very small drag)
        elem.velocity.x *= 0.999;
        elem.velocity.y *= 0.999;

        // Integrate position
        elem.position.x += elem.velocity.x * dt;
        elem.position.y += elem.velocity.y * dt;

        // Rotate based on angular velocity
        elem.rotation += elem.angular_velocity * dt * 57.2958; // rad→deg
        elem.angular_velocity *= 0.98; // damping

        elem.grounded = false;

        // ── Floor collision ──────────────────────────────────────────────────
        let bottom = elem.position.y + elem.height;
        if bottom >= ground {
            elem.position.y = ground - elem.height;
            elem.velocity.y = -(elem.velocity.y * elem.restitution);
            elem.velocity.x *= elem.friction;
            elem.angular_velocity *= 0.7;
            elem.grounded = true;

            // Stop micro-bouncing
            if elem.velocity.y.abs() < 20.0 {
                elem.velocity.y = 0.0;
            }
        }

        // ── Ceiling collision ────────────────────────────────────────────────
        if elem.position.y < ceil {
            elem.position.y = ceil;
            elem.velocity.y = -(elem.velocity.y * elem.restitution);
        }

        // ── Left wall ────────────────────────────────────────────────────────
        if elem.position.x < left {
            elem.position.x = left;
            elem.velocity.x = -(elem.velocity.x * elem.restitution);
        }

        // ── Right wall ───────────────────────────────────────────────────────
        let elem_right = elem.position.x + elem.width;
        if elem_right > right {
            elem.position.x = right - elem.width;
            elem.velocity.x = -(elem.velocity.x * elem.restitution);
        }
    }

    // Simple AABB collision between elements
    resolve_collisions(&mut world.elements);

    world.tick += 1;
}

/// Resolve pairwise AABB collisions (O(n²), fine for ≤200 elements)
fn resolve_collisions(elements: &mut Vec<PhysicsElement>) {
    let n = elements.len();
    for i in 0..n {
        for j in (i + 1)..n {
            let (a_pos, a_vel, a_w, a_h, a_mass, a_rest);
            let (b_pos, b_vel, b_w, b_h, b_mass, b_rest);
            {
                let a = &elements[i];
                let b = &elements[j];
                a_pos  = a.position;
                a_vel  = a.velocity;
                a_w    = a.width;
                a_h    = a.height;
                a_mass = a.mass;
                a_rest = a.restitution;
                b_pos  = b.position;
                b_vel  = b.velocity;
                b_w    = b.width;
                b_h    = b.height;
                b_mass = b.mass;
                b_rest = b.restitution;
            }

            // AABB overlap check
            let overlap_x = (a_pos.x + a_w).min(b_pos.x + b_w) - a_pos.x.max(b_pos.x);
            let overlap_y = (a_pos.y + a_h).min(b_pos.y + b_h) - a_pos.y.max(b_pos.y);

            if overlap_x <= 0.0 || overlap_y <= 0.0 {
                continue;
            }

            let restitution = (a_rest + b_rest) / 2.0;
            let total_mass = a_mass + b_mass;

            // Resolve along minimum penetration axis using proper elastic collision physics
            if overlap_x < overlap_y {
                // Horizontal collision
                let rel_vx = a_vel.x - b_vel.x;
                
                // Only resolve if moving towards each other
                if rel_vx > 0.0 {
                    // Calculate impulse for 1D elastic collision with restitution
                    let impulse = -(1.0 + restitution) * rel_vx / (1.0/a_mass + 1.0/b_mass);
                    
                    elements[i].velocity.x += impulse / a_mass;
                    elements[j].velocity.x -= impulse / b_mass;
                }

                // Separate to prevent sticking
                let sep = overlap_x / 2.0 + 0.5;
                if a_pos.x < b_pos.x {
                    elements[i].position.x -= sep;
                    elements[j].position.x += sep;
                } else {
                    elements[i].position.x += sep;
                    elements[j].position.x -= sep;
                }
            } else {
                // Vertical collision
                let rel_vy = a_vel.y - b_vel.y;
                
                // Only resolve if moving towards each other
                if rel_vy > 0.0 {
                    // Calculate impulse for 1D elastic collision with restitution
                    let impulse = -(1.0 + restitution) * rel_vy / (1.0/a_mass + 1.0/b_mass);
                    
                    elements[i].velocity.y += impulse / a_mass;
                    elements[j].velocity.y -= impulse / b_mass;
                }

                let sep = overlap_y / 2.0 + 0.5;
                if a_pos.y < b_pos.y {
                    elements[i].position.y -= sep;
                    elements[j].position.y += sep;
                } else {
                    elements[i].position.y += sep;
                    elements[j].position.y -= sep;
                }

                // Apply some friction on landing
                elements[i].velocity.x *= 0.92;
                elements[j].velocity.x *= 0.92;
            }
        }
    }
}

/// Return gravity acceleration vector (gx, gy) for current mode
pub fn gravity_vector(mode: GravityMode, g: f64, tick: u64) -> (f64, f64) {
    let mut rng = rand::thread_rng();
    match mode {
        GravityMode::Down  => (0.0, g),
        GravityMode::Up    => (0.0, -g),
        GravityMode::Left  => (-g, 0.0),
        GravityMode::Right => (g, 0.0),
        GravityMode::Zero  => (0.0, 0.0),
        GravityMode::Chaos => {
            // Chaotic gravity that rotates over time + random pulses
            let t = tick as f64 * 0.05;
            let cx = t.sin() * g * 0.8;
            let cy = t.cos() * g * 0.8;
            let jx = if rng.gen_bool(0.05) { rng.gen_range(-200.0..200.0) } else { 0.0 };
            let jy = if rng.gen_bool(0.05) { rng.gen_range(-200.0..200.0) } else { 0.0 };
            (cx + jx, cy + jy)
        }
    }
}

/// Give every element a random initial spin when gravity starts
pub fn apply_initial_impulse(world: &mut PhysicsWorld) {
    let mut rng = rand::thread_rng();
    for elem in &mut world.elements {
        // Small horizontal nudge for variety
        elem.velocity.x = rng.gen_range(-30.0..30.0);
        elem.angular_velocity = rng.gen_range(-2.0..2.0);
    }
}

/// Snap all elements back to their original positions
pub fn reset(world: &mut PhysicsWorld) {
    for elem in &mut world.elements {
        elem.position = elem.origin;
        elem.velocity = Vec2::zero();
        elem.rotation = 0.0;
        elem.angular_velocity = 0.0;
        elem.grounded = false;
    }
    world.tick = 0;
}

/// Run a full headless simulation and return all frames
pub fn simulate(
    world: &mut PhysicsWorld,
    duration_secs: f64,
    fps: u32,
) -> Vec<SimFrame> {
    apply_initial_impulse(world);

    let dt = 1.0 / fps as f64;
    let total_ticks = (duration_secs * fps as f64) as u64;
    let mut frames = Vec::with_capacity(total_ticks as usize);

    for _ in 0..total_ticks {
        step(world, dt);

        let energy: f64 = world.elements.iter().map(|e| e.kinetic_energy()).sum();
        let frame = SimFrame {
            tick: world.tick,
            time_secs: world.tick as f64 * dt,
            elements: world.elements.iter().map(|e| FrameElement {
                id:       e.id.clone(),
                x:        e.position.x,
                y:        e.position.y,
                vx:       e.velocity.x,
                vy:       e.velocity.y,
                rotation: e.rotation,
                grounded: e.grounded,
            }).collect(),
            total_energy: energy,
        };
        frames.push(frame);
    }

    frames
}
