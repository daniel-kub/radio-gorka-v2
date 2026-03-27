<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden" style="background-color: #0d0d2b;">
    <div v-if="logged" class="relative z-10 w-full max-w-4xl">
      <div class="neon-box rounded-lg p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-2xl font-bold neon-text">Propozycje utworów</h2>
            <p style="color: #FF1493;">Zarządzaj zgłoszeniami użytkowników</p>
          </div>
          <button
            @click="handleLogout"
            class="retro-button rounded-lg px-4 py-2 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            Wyloguj
          </button>
        </div>

        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin w-10 h-10 border-4 border-[#39FF14] border-t-transparent rounded-full" style="border-color: #39FF14;"></div>
        </div>

        <div v-else-if="results.length === 0 && eventResults.length === 0" class="text-center py-12">
          <p style="color: #39FF14; font-size: 1.5em;">Brak nowych propozycji</p>
        </div>

        <div v-else>
          <div v-if="results.length > 0">
            <h3 class="text-xl font-bold mb-4" style="color: #39FF14; font-family: 'Orbitron', sans-serif;">Propozycje zwykłe</h3>
            <ul class="flex flex-col gap-4 mb-8">
              <li
                v-for="(item, index) in results"
                :key="item.videoID"
                class="neon-box rounded-lg p-4 flex flex-col sm:flex-row items-center gap-4 hover:scale-[1.02] transition-transform cursor-pointer"
              >
                <a :href="'https://www.youtube.com/watch?v=' + item.videoID" target="_blank" class="shrink-0">
                  <img
                    :src="'https://img.youtube.com/vi/' + item.videoID + '/default.jpg'"
                    :alt="item.title"
                    class="w-24 h-24 sm:w-16 sm:h-16 rounded-lg object-cover"
                    style="box-shadow: 0px 0px 10px 2px #39FF14;"
                  />
                </a>
                <div class="flex-1 min-w-0 text-center sm:text-left">
                  <a :href="'https://www.youtube.com/watch?v=' + item.videoID" target="_blank" class="font-semibold truncate hover:underline block" style="color: #39FF14; font-family: 'Orbitron', sans-serif;">{{ item.title }}</a>
                  <p style="color: #FF1493;">{{ item.artist }}</p>
                  <p class="text-xs" style="color: #39FF14;">{{ item.videoID }}</p>
                </div>
                <div class="flex gap-2 w-full sm:w-auto">
                  <button
                    @click="accept(item, 'normal')"
                    class="retro-button-green rounded-lg px-3 py-2 shadow-lg flex items-center justify-center gap-1 flex-1 sm:flex-none text-sm"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                    </svg>
                    Akceptuj
                  </button>
                  <button
                    @click="reject(item, 'normal')"
                    class="retro-button rounded-lg px-3 py-2 shadow-lg flex items-center justify-center gap-1 flex-1 sm:flex-none text-sm"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                    Odrzuć
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="relative z-10 w-full max-w-md">
      <div class="neon-box rounded-lg p-8">
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 mb-4 neon-box-accent rounded-lg">
            <svg class="w-8 h-8" style="color: #39FF14;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <h2 class="text-2xl font-bold neon-text">Panel Administratora</h2>
          <p style="color: #FF1493;">Zaloguj się aby zarządzać</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium mb-2" style="color: #FF1493;">Login</label>
            <input
              type="text"
              v-model="username"
              class="retro-input rounded-lg px-4 py-3 w-full"
              placeholder="Wpisz login"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2" style="color: #FF1493;">Hasło</label>
            <input
              type="password"
              v-model="password"
              class="retro-input rounded-lg px-4 py-3 w-full"
              placeholder="Wpisz hasło"
              required
            />
          </div>

          <button
            type="submit"
            :disabled="loginLoading"
            class="retro-button rounded-lg px-6 py-3 shadow-lg w-full flex items-center justify-center gap-2"
          >
            <svg v-if="loginLoading" class="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <span>{{ loginLoading ? 'Logowanie...' : 'Zaloguj się' }}</span>
          </button>
        </form>

        <p v-if="loginError" class="mt-4 text-center" style="color: #FF1493;">
          {{ loginError }}
        </p>
      </div>
    
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const logged = ref(!!localStorage.getItem('token'));
const username = ref('');
const password = ref('');
const results = ref([]);
const eventResults = ref([]);
const loading = ref(false);
const loginLoading = ref(false);
const loginError = ref('');

onMounted(async () => {
  if (logged.value) {
    await fetchResults();
  }
});

const fetchResults = async () => {
  loading.value = true;
  try {
    const [normalRes, eventRes] = await Promise.all([
      axios.get("https://frog02-20689.wykr.es/api/list?token=" + localStorage.token),
      axios.get("https://frog02-20689.wykr.es/api/event/list?token=" + localStorage.token)
    ]);
    results.value = normalRes.data;
    eventResults.value = eventRes.data;
  } catch (error) {
    console.error(error);
    handleLogout();
  } finally {
    loading.value = false;
  }
};

const handleLogin = async () => {
  loginLoading.value = true;
  loginError.value = '';
  
  try {
    const response = await axios.post("https://frog02-20689.wykr.es/api/login", {
      username: username.value,
      password: password.value
    });

    const token = response.data.token;
    localStorage.setItem('token', token);
    logged.value = true;
    await fetchResults();
  } catch (error) {
    loginError.value = error.response?.data?.detail || 'Błąd logowania';
  } finally {
    loginLoading.value = false;
  }
};

const handleLogout = () => {
  localStorage.removeItem('token');
  logged.value = false;
  results.value = [];
  eventResults.value = [];
};

const accept = async (item, type) => {
  const endpoint = type === 'event' ? '/api/event/accept' : 'https://frog02-20689.wykr.es/api/accept';
  try {
    await axios.get(endpoint + "?token=" + localStorage.token + "&videoID=" + item.videoID);
    if (type === 'event') {
      eventResults.value = eventResults.value.filter(r => r !== item);
    } else {
      results.value = results.value.filter(r => r !== item);
    }
  } catch (error) {
    console.error(error);
  }
};

const reject = async (item, type) => {
  const reason = prompt("Podaj przyczynę odrzucenia:");
  if (reason === null) return;
  
  const endpoint = type === 'event' ? '/api/event/decline' : 'https://frog02-20689.wykr.es/api/decline';
  try {
    await axios.get(endpoint + "?token=" + localStorage.token + "&videoID=" + item.videoID + "&reason=" + encodeURIComponent(reason));
    if (type === 'event') {
      eventResults.value = eventResults.value.filter(r => r !== item);
    } else {
      results.value = results.value.filter(r => r !== item);
    }
  } catch (error) {
    console.error(error);
  }
};
</script>
