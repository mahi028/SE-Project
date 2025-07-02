import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue';
import router from './router';

import Aura from '@primeuix/themes/aura';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

import '@/assets/styles.scss';

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
const app = createApp(App);

app.use(pinia);
app.use(router);
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.app-dark'
        }
    }
});
app.use(ToastService);
app.use(ConfirmationService);

app.mount('#app');

router.beforeEach((to, from, next) => {
//   const loginStore = LoginStore() //Simulating role based access control

  if (to.meta.roles) {
    // const userRole = loginStore.role

    if ('hello') {
      next()
    } else {
      next({ name: 'NotFound' })
    }
  } else {
    next()
  }
})
