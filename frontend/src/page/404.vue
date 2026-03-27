<template>
  <div class="min-h-screen flex flex-col items-center justify-center py-12 px-4 relative overflow-hidden" style="background-color: #0d0d2b;">
    
    <div class="relative z-10 text-center flex flex-col items-center gap-6">
      <h1 class="text-5xl md:text-6xl font-bold" style="font-family: 'Orbitron', sans-serif; color: #39FF14; text-shadow: 0 0 20px #39FF14;">
        404
      </h1>

      <p class="text-xl md:text-2xl font-semibold" style="font-family: 'Orbitron', sans-serif; color: #FF1493;">
        Adrian Zandberg ukradł ci stronę
      </p>

      <div class="neon-box rounded-lg overflow-hidden" style="box-shadow: 0px 0px 30px 5px #FF1493;">
        <img
          src="https://media1.tenor.com/m/4Fyirtecr1MAAAAC/wkurwiony-zandberg-zandberg.gif"
          alt="zandberg nuh uh"
          class="w-72 h-auto rounded-lg"
        />
      </div>

      <router-link
        to="/"
        class="retro-button rounded-lg px-6 py-3 shadow-lg flex items-center gap-2"
        style="text-decoration: none;"
      >
        ← Wróć na stronę główną
      </router-link>
    </div>

    <p class="mt-10 relative z-10" style="color: #FF1493;">© Radio Górka</p>
  </div>
</template>