import { defineStore } from 'pinia'

export const useLoginStore = defineStore('loginDetails', {
  state: () => ({
    ezId: null,
    role: null,
    name: null,
    profileImageUrl: null,
  }),

  actions: {
    setLoginToken(token){
      localStorage.setItem('EZCARE-LOGIN-TOKEN', token)
    },

    setLoginDetails(details) {
      this.ezId = details.ezId
      this.role = details.role
      this.name = details.name
      this.profileImageUrl = details.profileImageUrl
    },

    clearLoginDetails() {
      this.ezId = null
      this.role = null
      this.name = null
      this.profileImageUrl = null
      localStorage.removeItem('EZCARE-LOGIN-TOKEN')
    },
  },
  persist: true,
})
