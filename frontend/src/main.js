import Vue from 'vue';
import axios from 'axios';
import VueClipboard from 'vue-clipboard2'
import VueGoodTablePlugin from 'vue-good-table'

import 'vue-good-table/dist/vue-good-table.css'

Vue.use(VueClipboard)
Vue.use(VueGoodTablePlugin)


let base_url = ''
if (process.env.NODE_ENV == 'development') {
  base_url = 'http://localhost:5000/'
}

var axios_cfg = function(url, data='', type='form') {
  if (data == '') {
    return {
      method: 'get',
      url: base_url + url
    };
  } else if (type == 'form') {
    return {
      method: 'post',
      url: base_url + url,
      data: data,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    };
  } else if (type == 'file') {
    return {
      method: 'post',
      url: base_url + url,
      data: data,
      headers: { 'Content-Type': 'multipart/form-data' }
    };
  }
};

new Vue({
  el: '#app',
  data: {
    columns: [
      {
        label: 'Name',
        field: 'distinguished_name',
        // filterable: true,
      },
      {
        label: 'Flag',
        field: 'flag',
        filterable: true,
      },
      {
        label: 'Expiration Date',
        field: 'expiration_date',
        type: 'date',
        dateInputFormat: 'yyyy-MM-dd HH:mm:ssxxxxx',
        dateOutputFormat: 'yyyy-MM-dd HH:mm:ssxxxxx',
      },
      {
        label: 'Revocation Date',
        field: 'revocation_date',
        type: 'date',
        dateInputFormat: 'yyyy-MM-dd HH:mm:ssxxxxx',
        dateOutputFormat: 'yyyy-MM-dd HH:mm:ssxxxxx',
      },
      {
        label: 'Actions',
        field: 'actions',
        sortable: false,
        tdClass: 'text-right',
        globalSearchDisabled: true,
      },
    ],
    rows: [],
    actions: [
      {
        name: 'u-revoke',
        label: 'Revoke',
        showWhenFlag: 'V'
      },
      {
        name: 'u-unrevoke',
        label: 'Unrevoke',
        showWhenFlag: 'R'
      },
      {
        name: 'u-show-config',
        label: 'Show config',
        showWhenFlag: 'V'
      },
      {
        name: 'u-download-config',
        label: 'Download',
        showWhenFlag: 'V'
      }
    ],
    u: {
      data: {},
      newUserName: '',
      modalNewUserVisible: false,
      modalShowConfigVisible: false,
      openvpnConfig: ''
    }
  },
  watch: {
    // u: function () {
    //   this.u.columns = Object.keys(this.u.data[0]) //.reverse()
    // }
  },
  mounted: function () {
    this.u_get_data()
  },
  created() {
    var _this = this
    this.$root.$on('u-revoke', function (msg) {
      axios.request(axios_cfg('api/v1/user/revoke?user=' + _this.username))
      .then(function(response) {
        console.log(response.data);
        _this.u_get_data();
      });
    })
    this.$root.$on('u-unrevoke', function () {
      axios.request(axios_cfg('api/v1/user/unrevoke?user=' + _this.username))
      .then(function(response) {
        console.log(response.data);
        _this.u_get_data();
      });
    })
    this.$root.$on('u-show-config', function () {
      this.u.modalShowConfigVisible = true;
      axios.request(axios_cfg('api/v1/user/showcfg?user=' + _this.username))
      .then(function(response) {
        _this.u.openvpnConfig = response.data;
      });
    })
    this.$root.$on('u-download-config', function () {
      window.open(base_url + 'api/v1/user/downloadcfg?user=' + _this.username, "_blank");
    })
  },
  computed: {
    // uCtxStyle: function () {
    //   return {
    //     'top': this.u.ctxTop + 'px',
    //     'left': this.u.ctxLeft + 'px'
    //   }
    // }
  },
  methods: {
    rowStyleClassFn: function(row) {
      return row.connection_status == '' ? '' : 'active-row';
    },
    rowActionFn: function(e) {
      this.username = e.target.dataset.username
      console.log(this.username)
      this.$root.$emit(e.target.dataset.name)
    },
    u_get_data: function() {
      var _this = this;
      axios.request(axios_cfg('api/v1/users/list'))
      .then(function(response) {
        _this.u.data = response.data
        _this.rows = response.data
      });
    },
    create_user: function() {
      var _this = this;
      axios.request(axios_cfg('api/v1/user/create?user=' + this.u.newUserName))
      .then(function(response) {
        _this.u_get_data();
        _this.u.newUserName = '';
      });
    }
  }
})
