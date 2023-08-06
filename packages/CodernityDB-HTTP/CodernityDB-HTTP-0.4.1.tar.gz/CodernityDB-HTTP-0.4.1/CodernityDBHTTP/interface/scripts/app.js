/*
 Copyright 2011-2012 Codernity (http://codernity.com)

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */


(function() {

    var my_cms = {};
    var error_marker = null;
    $.ajaxSetup({
        "contentType": "application/json",
    })

    $(document).ajaxError( function(event, jqXHR, ajaxSettings, thrownError) {
        Notifier.error(jqXHR.responseText, jqXHR.status + ': ' + thrownError)
        console.log('status: ' + jqXHR.status)
        console.log('responseText: ' + jqXHR.responseText)
        console.log('thrownError: ' + thrownError)
        console.log('event:')
        console.log(event)
        console.log('ajaxSettings:')
        console.log(ajaxSettings)
        
        if(jqXHR.status == 400 && (ajaxSettings['url'] == '/add_index' || ajaxSettings['url'] == '/edit_index')) {
            var ls = $.parseJSON(jqXHR.responseText)['reason']
            ls = RegExp('\\(in line: ([0-9]+)\\)').exec(ls)
            if (error_marker) {
                error_marker.clean()
            }
            if (ls){
                error_marker = my_cms['index_code'].markText({line : ls[1]-1,ch : 0},{line : ls[1]-1,ch : 99999},"cm-error")
            }
        }
    })

    $('#indexDetailsNavigation').live('click', function(){
        $('div.popover').remove();
    });

    ko.bindingHandlers.codeMirror = function() {
        return {
            init: function(element, valueAccessor, allBindingsAccessor, context) {
              var options = allBindingsAccessor().codeMirrorOptions || {}
              var modelValue = valueAccessor()
              var value = ko.utils.unwrapObservable(valueAccessor())
              var el = $(element)

              setTimeout(function() {
                      options.onChange = function(from, to, text, next) {
                      if (ko.isWriteableObservable(modelValue)) {
                      modelValue(my_cms[el.attr('id')].getValue())
                      }
                      }
                      my_cms[el.attr('id')] = CodeMirror.fromTextArea(element, options)

                      if(value) {
                      my_cms[el.attr('id')].setValue(value)
                      }
                      }, 0)

          ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                  setTimeout(function(){
                      my_cms[el.attr('id')].toTextArea()
                      }, 0)
                  });

      }
      , update: function(element, valueAccessor) {
          var el = $(element)
              var value = ko.utils.unwrapObservable(valueAccessor())
              var id = el.attr('id')
              var update = function(val) {
                  var update_tries = 0
                      function later() {
                          setTimeout(function() {
                                  updater()
                                  }, 5)
                      }
                  function updater() {
                      if(!my_cms[el.attr('id')]) {
                          update_tries++
                              if (update_tries < 5) {
                                  later()
                              } else {
                                  console.log("Failed to activate codemirror")
                              }
                      } else {
                          if (val != null) {
                              if(val != my_cms[el.attr('id')].getValue()) {
                                  my_cms[el.attr('id')].setValue(val)
                              }
                          }
                          if (error_marker) {
                              error_marker.clear()
                              error_marker = null
                          }
                      }
                  }
                  return updater
              }
          if (id !== undefined && id !== '') {
              var upd = update(value)
                  upd()
          }
      }
        }
    }()

    // my validators
    kk.validators.NotEqualI = (function() {
        function NotEqualI(word, message) {
            this.word = word
            this.message = message || ("Can't use this value");
        }

        NotEqualI.prototype.validate = function(value) {
            value = ko.utils.stringTrim(value != null ? value.toString() : '');
            return this.word.toLowerCase() != value.toLowerCase()
          };
        return NotEqualI;
    })();

    var application = null

    var FullSingleDoc = function(id, dummy) {
        var self = this


        self._id = ko.observable(id)
        self._rev = ko.observable(null)
        self.document_data = ko.observable()
        //self._index = ko.observable(index || 'id')

        self.fetch = function() {
            $.get('/get/id', {'key': JSON.stringify(self._id())},
                function(data) {
                self._rev(data._rev)
                self.document_data(JSON.stringify(data, null, 4))
                }
            )
        }

        self.save = function() {
            if(self._id()) {
                self.update_doc()
            } else {
                self.create_doc()
            }
        }

        self.create_doc = function() {
            try {
                var data = JSON.parse(self.document_data())
            } catch(err) {
                Notifier.error("Please provide content in JSON format.")
            }
            if(data) {
                $.post('/insert',JSON.stringify({"data": data}),
                    function(data) {
                        application.add_info("Inserted, new id" + data._id + ", rev: " + data._rev)
                        location.hash = "#doc/" + data._id
                    }
                )
            }
        }

        self.update_doc = function() {
            try {
                var data = JSON.parse(self.document_data())
            } catch(err) {
                Notifier.error("Please provide content in JSON format.")
            }
            if(data) {
                $.post('/update',JSON.stringify({"data": data}),
                    function(data) {
                        application.add_info("Updated, new rev: " + data._rev)
                        self.fetch()
                    }
                )
            }
        }

        self.delete_doc = function() {
            if(self._id) {
                $.post('/delete', JSON.stringify({"data": {"_id": self._id(), "_rev": self._rev()}}),
                    function(data) {
                        history.back()
                    }
                )
            }
        }

        self.revert_doc = function() {
            self.fetch()
        }

        if (!dummy) {
            self.fetch()
        }
    }

    var SmallSingleDoc = function(small_doc) {
        var self = this

        self.small_doc = small_doc

        self.get = function() {
            location.hash = "#doc/" + self.small_doc._id
        }

    }

    var SingleIndexDetails = function(name) {
        var self = this
        self.name = name //ko.observable(name)
        self.index_code = ko.observable('')
        self.index_details = ko.observableArray([])
        self.show_code = ko.observable(null)
        self.class_names = ko.observableArray([])
        self.class_name = ko.observable('')
        self.is_normal_code = ko.observable(true)
         
        if (name == null) {
            self.simplified_code = ""
            self.python_code = ""
        }

        self.validation = new kk.Validation( self, {
            form_name : [   new kk.validators.Required("Enter name"),
                            new kk.validators.NotEqualI("id", "Can't use 'id'")],
        })

        self.open_save_modal = function() {
            // look for classes in index code
            if (self.is_normal_code()) {
                var classes = self.index_code().match(/^class\s+[a-zA-Z_]\w*[\(|:]/gm)

                    if(!classes) {
                        application.add_error("Can't find any index class in your code.")
                            return
                    }

                // ['class Klass(', ['class Klass2:']] => ['Klass', 'Klass2']
                for (var i = 0; i < classes.length; i++) classes[i] = classes[i].split(' ')[1].slice(0, -1)
                    classes = ko.utils.arrayGetDistinctValues(classes)
                        self.class_names(classes)
                        self.class_name(classes[0])

                $("#save_plain_modal").modal('show')
            } else {
                self._create()
            }
        }


        self.open_save_edit_modal = function() {
            if (self.is_normal_code()) {
                // look for classes in index code
                var classes = self.index_code().match(/^class\s+[a-zA-Z_]\w*[\(|:]/gm)

                    if(!classes) {
                        application.add_error("Can't find any index class in your code.")
                            return
                    }

                // ['class Klass(', ['class Klass2:']] => ['Klass', 'Klass2']
                for (var i = 0; i < classes.length; i++) classes[i] = classes[i].split(' ')[1].slice(0, -1)
                    classes = ko.utils.arrayGetDistinctValues(classes)
                        self.class_names(classes)
                        self.class_name(classes[0])

                $("#save_edit_plain_modal").modal('show')
            } else {
                self._edit()
            }
        }

        self.switch_new_code = function () {
            if (self.is_normal_code()) {
                self.python_code = self.index_code()
                self.index_code(self.simplified_code)
            } else {
                self.simplified_code = self.index_code()
                self.index_code(self.python_code)
            }
            self.is_normal_code(!self.is_normal_code())
        }

        self.save = function() {
            if (self.name) {
                if (self.name === 'id') {
                    application.add_error("Id index can't be changed")
                }
                $("#save_edit_plain_modal").modal('hide')
                self._edit()
            } else {
                self.validation.validate()
                if (self.validation.isValid()) {

                    self.inject_metadata()
                    $("#save_plain_modal").modal('hide')

                    self._create()
                }
            }
        }

        self.inject_metadata = function() {
            var header_footer = "# end of generated metadata"

            var code_header = "# " + self.form_name() + "\n"
            code_header += "# " + self.class_name() + '\n'
            code_header += header_footer + "\n"
            var code = ''
            if(self.index_code().split('\n')[2].indexOf(header_footer) == 0)
                code = self.index_code().split('\n').splice(4).join('\n')
            else
                code = self.index_code()

            code = code_header + code
            self.index_code(code)
        }

        self.insert_plain = function(){
            $.get('/get_index_header')
            .success(function(data) {
                    /*console.log(data)*/
                lines = data.split('\n')
                /*console.log(self.index_code())*/
                self.index_code(lines.slice(3).join('\n'))
            })
        }

        self.show_code.subscribe(function(newValue) {
            if(!newValue) {
                self.get_details()
            }
        })

        self.is_normal_code.subscribe(function(newValue){
            if(my_cms['index_code']){
                my_cms['index_code'].setOption('mode',self.is_normal_code() ? 'python' : 'text')
            }
        })
        
        self.get_index_code = function() {
            $.get('/get_index_code/' + self.name ,{code_switch : JSON.stringify("S")}, function(data) {
                if(!self.is_normal_code()){
                    self.index_code(data)
                }
                self.simplified_code = data
                })
            $.get('/get_index_code/' + self.name,{code_switch : JSON.stringify("P")}, function(data) {
                if (self.is_normal_code()){
                    self.index_code(data)
                }
                self.python_code = data
                })

            if(application.index_changed != null) {
                $('button.btn-reindex').popover({"placement": "top", title: application.index_changed}).popover('show')
                application.index_changed = null
            }
        }

        self.get_index_template = function() {
            $.get('/get_index_header', {}, function(data) {
                self.index_code(data)
            })
        }

        self.count_all = function() {
            $.get('/count/all', {'index_name': JSON.stringify(self.name)},
                function(data) {
                    var message
                    if (data == 0) message = 'Found nothing'
                    else if (data == 1) message = 'Found 1 item.'
                    else message = 'Found ' + data + ' items.'
                    application.add_info(message)
                }
            )
        }

        self._create = function(upd) {
            var code = self.index_code()
            $.post('/add_index', JSON.stringify({new_index: code}),
                function(data) {
                    self.name = data
                    application.add_info("Created index, name = " + self.name)
                    application.index_changed = "New index"
                    location.hash = '#index/' + self.name + '/details'
                }
            )
        }

        self._edit = function() {
            var code = self.index_code()
            $.post('/edit_index', JSON.stringify({index: code}),
                function(data) {
                    self.name = data
                    application.add_info("Edited index, name = " + self.name)
                    application.index_changed = "Index changed"
                    location.hash = '#index/' + self.name + '/details'
                    self.get_index_code()
                }
            )
        }

        self.reindex = function() {
            if (!self.name) {
                application.add_error("Can't reindex non existing index")
            } else if (self.name == 'id') {
                application.add_error("Id index can't be reindexed")
            } else {
                $.get('/reindex_index/' + self.name, {},
                    function(data) {
                        application.add_info("Reindexed")
                        self.get_details()
                    }
                )
            }
        }

        self.compact = function() {
            if (!self.name) {
                application.add_error("Can't compact non existing index")
            } else {
                $.get("/compact_index/" + self.name, {},
                    function(data) {
                        application.add_info("Compacted")
                        self.get_details()
                    }
                )
            }
        }

        self.destroy = function() {
            if (!self.name) {
                application.add_error("Can't delete non existing index")
            } else if (self.name == 'id') {
                application.add_error("Id index can't be destroyed")
            } else {
                $.get('/destroy_index/' + self.name, {},
                    function(data) {
                        self.name = null
                        location.hash = "#"
                    }
                )
            }
        }

        self.view = function() {
            if (!self.name) {
                application.add_error("Can't view non existing index")
            } else {
                location.hash = "#index/" + self.name + '/all/0'
            }
        }

        self.get_details = function() {
            if(self.name) {
                $.get('/get_index_details/' + self.name,
                    function(data) {
                        var det = []
                        $.each(data, function(key, value) {
                            det.push([key, value])
                        })
                        det.sort(function(a, b) {return a[0] < b[0]})
                        self.index_details(det)
                    }
                )
            }
        }

        self.toggle_code_details = function() {
            if (!self.name) {
                application.add_error("Can't get details/code of non existing index")
            } else {
                self.show_code(!self.show_code())
                if(!self.show_code()) {
                    self.get_details()
                } else { // XXX: fix it
                    setTimeout(function() {
                        my_cms['index_code'].setOption('mode',self.is_normal_code() ? 'python' : 'text')}, 0)
                }
            }
        }
        

        self.switch_code = function () {
            if (self.is_normal_code()) {
                $.get('/get_index_code/' + self.name ,{code_switch : JSON.stringify("S")}, function(data) {
                    self.simplified_code = data 
                    self.index_code(data)
                    })
            } else {
                $.get('/get_index_code/' + self.name ,{code_switch : JSON.stringify("P")}, function(data) {
                    self.python_code = data 
                    self.index_code(data)
                    })
            }
            self.is_normal_code(!self.is_normal_code())
        }

        self.code_details_text = function() {
            if (!self.show_code()) {
                return "Show code"
            }
            return "Show details"
        }

        self.show_code(false)

        if(self.name) {
            self.get_index_code()
        }

    }

    var SingleIndex = function(name, page) {
        var self = this

        self.on_page_options = [10, 20, 50, 100]
        self.on_page = ko.observable(application.on_page)
        self.page = page || 0

        self.lo = [application.on_page, 0]
        if (page) {
            self.lo = [self.lo[0], self.lo[1] + (self.lo[0] * page)]
        }

        self.name = name
        self.docs = ko.observableArray()

        self.map_to_docs = function(docs) {
            self.docs(ko.utils.arrayMap(docs, function(doc) {
                return new SmallSingleDoc(doc)
            }))
        }

        self.get_all = function(limit, offset) {
            if (!limit && !offset) {
                limit = self.lo[0]
                offset = self.lo[1]
            }
            self.lo = [limit, offset]
            $.post('/all/' + self.name
                , JSON.stringify({limit: limit + 1, offset: offset, with_doc: false, with_storage: false})
                , function(docs) {
                    if (docs) {
                        if(docs.length == 0) {
                            if (self.current_page() > 0) {
                                location.hash = "#index/" + self.name + "/all/" + (self.current_page() - 1)
                                return
                            }
                        }
                    }
                    self.map_to_docs(docs)
                })
        }

        self.get_docs = function() {
            var docs = self.docs()
            if (!docs) {return null}
            if (docs.length > self.lo[0]) {
                docs.pop()
            }
            return docs
        }

        self.current_page = function() {
            var x = self.lo[1] / self.lo[0]
            return x
        }

        self.has_previous = ko.computed(function() {
            return (self.lo[1] - self.lo[0]) >= 0
        }, this)

        self.has_next = ko.computed(function() {
            if(self.docs()) {
                return self.docs().length > self.lo[0]
            }
            return false
        }, this)

        self.show_previous = function() {
            location.hash = "#index/" + self.name + '/all/' + (self.current_page() - 1)
        }

        self.show_next = function() {
            location.hash = "#index/" + self.name + '/all/' + (self.current_page() + 1)
        }

        self.show_all = function() {
            location.hash = "#index/" + self.name + "/all/0"
        }

        self.show_details = function() {
            location.hash = "#index/" + self.name + "/details"
        }

        self.on_page.subscribe(function(newValue) {
            first = application.on_page * self.page
            application.on_page = newValue
            new_page = Math.floor(first / newValue)
            new_address = "#index/" + self.name + "/all/" + new_page

            if (location.hash == new_address) {
                application.sammy.refresh()
            }
            else {
                location.hash = new_address
            }

        })

    }

    var About = function(version) {
        var self = this
        self.version = ko.observable(version)
    }

    var Start = function() {
        var self = this
    }

    function DBViewModel() {
        var self = this

        self.indexes = ko.observableArray(null)
        self.chosenIndex = ko.observable(null)
        self.singleDoc = ko.observable(null)
        self.singleIndexDetails = ko.observable(null)
        self.newIndex = ko.observable(null)
        self.dbInit = ko.observable(null)
        self.dbCreate = ko.observable(null)
        self.dbOpen = ko.observable(null)
        self.dbDetails = ko.observableArray(null)
        self.about = ko.observable(null)
        self.database_path = ko.observable('')
        self.on_page = 10   // how many items on page initially
        self.index_changed = null //is index just created?
        self.is_database_opened = false
        self.is_database_exist = ko.observable(false)
        self.database_path = ko.observable(null)
        self.accessibleWithoutDb = [
            '#about',
            '#db/start',
            '#db/details'
        ]
        self.notAccessibleWithClosedDb = [
            '#doc/create_new'
        ]
        self.notAccessibleWithOpenedDb = [
            '#db/init'
        ]

        self.get_indexes_names = function() {
            $.ajax({
                url: '/get_indexes_names',
                async: false,
                success: function(indexes) {
                    self.indexes(ko.utils.arrayMap(indexes, function (index) {
                        return new SingleIndex(index)
                    }))
                }
            });
        }

        self.db_init = function() {
            if(self.is_database_exist()) {
                return self.open()
            }
            return self.create()
        }

        self.can_display_page = function() {
            if(self.indexes().length == 0 && location.hash != '#db/init') {
                self.database_exist(function(status) {
                    if (!status && $.inArray(location.hash, self.accessibleWithoutDb) == -1) {
                        self.clean_iface('#db/init')
                        location.hash = '#db/init'
                    }
                })
            }
            if ($.inArray(location.hash, self.notAccessibleWithClosedDb) != -1) {
                self.database_opened(function(status) {
                    if (!status) {
                        self.clean_iface('#db/init')
                        location.hash = '#db/init'
                    }
                })
            } else if ($.inArray(location.hash, self.notAccessibleWithOpenedDb) != -1) {
                self.database_opened(function(status) {
                    if (status) {
                        self.clean_iface('#db/details')
                        location.hash = '#db/details'
                    }
                })
            }
        }

        self.get_index = function(name, page, without_docs) {
            var ind = new SingleIndex(name, page)
            self.chosenIndex(ind)
            if(!without_docs) {
                ind.get_all()
            }
        }

        self.get_index_details = function(name) {
            var ind = new SingleIndexDetails(name)
            self.singleIndexDetails(ind)
        }

        self.add_new_index = function() {
            var ind = new SingleIndexDetails(null)
            self.newIndex(ind)
        }

        self.database_exist = function(callback) {
            $.get('/exists', {},
                function(status) {
                    self.is_database_exist(status)
                    callback(status)
                }
            )
        }

        self.database_opened = function(callback) {
            $.get('/opened', {},
                function(status) {
                    callback(status)
                }
            )
        }

        self.init_database = function() {
            self.get_db_details()
            self.dbInit(new Start())
        }

        self.create_database = function() {
            self.dbCreate(new Start())
        }

        self.open_database = function() {
            self.dbOpen(new Start())
        }

        self.create = function(form) {
            $.post('/exists', JSON.stringify({"path": self.database_path()}),
                function(status) {
                    if(status == true) {
                        self.open()
                    } else {
                        $.post('/create', JSON.stringify({"path": self.database_path()}))
                        .complete(function(status) {
                            self.indexes.removeAll()
                            self.get_indexes_names()
                            self.clean_iface('#db/details')
                            location.hash = '#db/details'
                        })
                        .success(function() {application.add_success('Database created')})
                        .error(function() {application.add_error('Could not create database')})
                    }
                }
            )
        }

        self.get_db_details = function(display) {
            self.database_opened(function(status) {
                self.is_database_opened = status
                $.get('/get_db_details', {},
                    function(details) {
                        var det = []
                          , env = []
                        $.each(details, function(k, v) {
                            if(k === 'path') {
                                if (v != null) {
                                    self.database_path(v)
                                }
                            }
                            if(k === 'cdb_environment') {
                                $.each(v, function(kk, vv) {
                                    env.push([kk, vv])
                                })
                            } else {
                                det.push([k, v])
                            }
                        })
                        det.sort(function(a, b) {return a[0] < b[0]})
                        if(display) {
                            self.dbDetails([det, env])
                        }
                    }
                )
            })
        }

        self.open = function() {
            $.post('/open', JSON.stringify({"path": self.database_path()}))
            .complete(function(status) {
                self.indexes.removeAll()
                self.get_indexes_names()
                self.clean_iface('#db/details')
                location.hash = '#db/details'
            })
            .success(function() {application.add_success('Database opened')})
            .error(function() {application.add_error('Could not open database')})
        }

        self.close = function() {
            $.get("/close")
            .complete(function() {
                self.indexes.removeAll()
                self.get_db_details(true)
            })
            .success(function() {application.add_success('Database closed')})
            .error(function() {application.add_error('Could not close database')})
        }

        self.destroy = function() {
            $.get("/destroy")
            .complete(function() {
                self.is_database_exist(false)
                location.hash = '#db/init'
            })
            .success(function() {application.add_success('Database destroyed')})
            .error(function() {application.add_error('Could not destroy database')})
        }

        self.reindex = function() {
            $.get("/reindex")
            .complete(function() {self.get_db_details(true)})
            .success(function() {application.add_success('Reindexed')})
            .error(function() {application.add_error('Could not reindex')})
        }

        self.compact = function() {
            $.get('/compact')
            .complete(function() {self.get_db_details(true)})
            .success(function() {application.add_success('Compacted')})
            .error(function() {application.add_error('Could not compact')})
        }

        self.get_single_doc = function(doc_id) {
            self.singleDoc(new FullSingleDoc(doc_id))
        }

        self.create_new_doc = function() {
            self.singleDoc(new FullSingleDoc(null, true))
        }

        self.has_indexes_names = function() {
            if (!self.indexes() || 1 == 1) { //TODO: index modifications / deletions, should refresh
                return self.get_indexes_names()
            }
        }

        self.get_current_viewing = function() {
            if (self.singleDoc() != null) {
                return self.singleDoc()._id
            } else {
                return ""
            }
        }

        self.get_about = function(name) {
            $.get('/get_version', {})
            .success(function(version) {
                self.about(new About(version))
            })
        }

        self.navigate_to_form = function(doc_id) {
            location.hash = "#doc/" + doc_id
        }

        self.add_success = function(content) {
            Notifier.success(content)
        }

        self.add_info = function(content) {
            Notifier.info(content)
        }

        self.add_warning = function(content) {
            Notifier.warning(content)
        }

        self.add_error = function(content) {
            Notifier.error(content)
        }

        self.add_notify = function(content) {
            Notifier.notify(content)
        }

        self.clean_iface = function(page_to_show) {
            self.about(null)
            if(page_to_show != '#db/init') {
                self.dbInit(null)
            }
            if(page_to_show != '#db/create') {
                self.dbCreate(null)
            }
            if(page_to_show != '#db/open') {
                self.dbOpen(null)
            }
            self.chosenIndex(null)
            self.singleDoc(null)
            self.singleIndexDetails(null)
            self.database_path('')
            if (self.newIndex() != null) {
                self.newIndex(null)
            }
            if(page_to_show != '#db/details') {
                self.dbDetails(null)
            }
        }

        // routes
        setTimeout(function() {

            self.sammy = Sammy(function() {

                // some global cleanups and checks...
                this.before({}, function() {
                    // Dropdown clearMenus() is not called when we using Sammy.js...
                    $('[data-toggle="dropdown"]').parent().removeClass('open')
                    $('div.popover').remove()
                    self.has_indexes_names()
                    self.clean_iface()
                })

                this.get("#db/init", function() {
                    self.init_database()
                })

                this.get("#db/details", function() {
                    self.get_db_details(true)
                })

                this.get("#index/:index/all/:page", function() {
                    var p = parseInt(this.params.page)
                    if(p == NaN) {
                        location.hash = "#index/" + this.params.index + "/all/0"
                    } else {
                        self.get_index(this.params.index, p)
                    }
                })

                this.get('#index/create_new', function() {
                    self.add_new_index()
                })

                this.get("#index/:index/all", function() {
                    location.hash = "#index/" + this.params.index + "/all/0"
                })

                this.get("#index/:index/details", function() {
                    self.get_index_details(this.params.index)
                })

                this.get("#doc/create_new", function() {
                    self.create_new_doc()
                })

                this.get("#doc/:doc_id", function() {
                    self.get_single_doc(this.params.doc_id)
                })

                this.get("#navigator", function() {
                    self.navigate_to_form(this.params['location'])
                })

                this.get("#about", function() {
                    self.get_about()
                })

                this.get('', function() {
                    location.hash = '#db/details'
                })

                this.after(function(){
                    self.can_display_page()
                })

            }).run()
        }, 0)
    }

    application = new DBViewModel()

    ko.applyBindings(application)
})()
