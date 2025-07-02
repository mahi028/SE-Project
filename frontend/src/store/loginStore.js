import { defineStore } from 'pinia'

export const useLoginStore = defineStore('loginDetails', {
  state: () => ({
    ez_id: null,
    role: null,
  }),

  actions: {
    setLoginDetails(details) {
      this.ez_id = details.ez_id
      this.role = details.role
    },

    clearLoginDetails() {
      this.ez_id = null
      this.role = null
    },
  },
  persist: true,
})
