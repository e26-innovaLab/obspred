// Generador pseudo-aleatorio determinístico: misma semilla → mismos valores.
// Se usa para que los datos mock sean estables entre renders (no "parpadean"
// al cambiar de pestaña y volver) sin necesitar un backend todavía.

function hashSeed(seed: string): number {
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h << 5) - h + seed.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

export function seededRandom(seed: string): number {
  const h = hashSeed(seed);
  const x = Math.sin(h) * 10000;
  return x - Math.floor(x);
}

export function seededRange(seed: string, min: number, max: number): number {
  return min + seededRandom(seed) * (max - min);
}

export function seededInt(seed: string, min: number, max: number): number {
  return Math.floor(seededRange(seed, min, max + 1));
}
