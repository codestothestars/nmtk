define(['underscore','leaflet'], function (_, L) {
	"use strict";
	var controller=['$scope','$routeParams','$location','$log','$http',
	                '$timeout','$rootScope',
        /*
		 * A variant of the ViewResults Controller that uses leaflet-directive 
		 * rather than leaflet directly.
		 */
	        
		function ($scope, $routeParams, $location, $log, $http, $timeout, $rootScope) {
			$scope.jobid=$routeParams.jobid;
			$scope.$parent.results_job=$scope.jobid;
			$scope.changeTab('results');
			$scope.filterOptions= { filterText: "",
									userExternalFilter: true };
							
			$scope.totalServerItems=0;
			$scope.selections=[];
			$scope.page_size=100;
			$scope.pagingOptions= {
			};
			$scope.columnOptions=[];
			$scope.sortInfo= { fields: ['nmtk_id'],
							   directions: ['asc'] };

			/*
			 * Note: This relies on leaflet being available...
			 */
			function getBounds(bbox) {
				var southWest = new L.LatLng(bbox[2], bbox[0]);
				var northEast = new L.LatLng(bbox[3], bbox[1]);	
				return {'southWest': southWest,
					    'northEast': northEast};
				// The Angular directive stuff doesn't use the leaflet bbox stuff
			    // correctly, so we'll hackify it slightly to ensure compatibility with
				// both...
				var bbox=L.LatLngBounds(southWest, northEast);
				bbox.southWest=southWest;
				bbox.northEast=northEast;
				return bbox
			}
			
			$scope.$on('ngGridEventScroll', function (e) {
				$log.info('Got paging event', e);
				$scope.getPagedDataAsync($scope.page_size, $scope.paging_offset+$scope.page_size,
						                 $scope.filterOptions.filterText,$scope.sort_field);
			});
		            				
			
			$scope.getPagedDataAsync=function(pageSize, offset, searchText, order){
				$scope.paging_offset=offset;
				if ($scope.job_data) {
					var options={offset: offset,
							     limit: pageSize,
							     search: searchText,
							     order_by: order,
							     format: 'pager'};
					$log.info('Making request for ', $scope.job_data.results, options);
					$http.get($scope.job_data.results, {params: options}).success(function (data) {
						$scope.totalServerItems=data.meta.total;
						$scope.pagingOptions.currentPage=(data.meta.offset/data.meta.limit)+1
						if ($scope.paging_offset > 0) {
							$log.info('Concatenating!')
							$scope.data= $scope.data.concat(data.data);
		//					$scope.data.push.apply($scope.data, data.data);
						} else {
							$scope.data=data.data;
						}
						if ($scope.columnOptions.length == 0) {
							$scope.columnOptions=[]
							var visible=false;
							var fields=JSON.parse($scope.input_data.fields);
							fields.push('nmtk_feature_id');
							_.each(data.data[0], function (col_val, col_name) {
								if (_.indexOf(fields, col_name) == -1) {
									visible=true;
								} else {
									visible=false;
								}
								$scope.columnOptions.push({ field: col_name,
									                        visible: visible });
							});
							$log.info($scope.columnOptions);
						}
					});
				}
			};
			$scope.olcount=0;
			
			// Whenever a feature is selected in the table, we will match that feature in
			// the view window...
			$scope.$watch('selected_features', function (newVal, oldVal) {
				var ids=[];
				_.each($scope.selected_features, function (data) {
					ids.push(data.nmtk_id);
				});
				if ($scope.leaflet.layers.overlays['highlight' + $scope.olcount]) {
					delete $scope.leaflet.layers.overlays['highlight'+$scope.olcount];
				}
				$scope.olcount += 1;
				if (ids.length) {
						$scope.leaflet.layers.overlays['highlight'+$scope.olcount]= {
					            name: 'Selected Layers',
					            type: 'wms',
					            visible: true,
					            url: $scope.job_data.wms_url,
					            layerOptions: { layers: "highlight",
					            	            ids: ids.join(','),
					                    		format: 'image/png',
					                    		transparent: true }
					    }
					}
				$log.info('Got items selected!');
				// If nothing is selected, select the first item
				if ($scope.selected_selected.length == 0) {
					$timeout(function () {
						$scope.gridOptions2.selectItem(0, true);
					}, 100);
				}
			}, true);
			
			// When someone selects items via the "results" grid it goes
			// into selections, which we then need to copy over to selected_features
			
			$scope.$watch('selections', function (newVal, oldVal) {
				$log.info('Got selections!')
				// If we're working with results from a map-click, then clicking on
				// a row will remove those results.
				if ($scope.feature_query_results) {
					$scope.selected_features=[];
					$scope.selected_selected.length=0;
					$scope.feature_query_results=false;
				}
				var ids=[]
				_.each($scope.selected_features, function (data) {
					ids.push(data.nmtk_id);
				});
				if (! $scope.selected_features) {
					$scope.selected_features=newVal;
				} else {
					_.each(newVal, function (data) {
						if (! _.contains(ids, data.nmtk_id)) {
							$scope.selected_features.push(data);
						}
					})
				}
		//		$scope.selected_features=newVal;
			},true);
			
			// We watch reloadData to signal to ng-grid that it should reset its 
			// selections and reload data.  This is because Ng-grid does not have a
			// method by which we can *unselect* selected rows (easily.)
			$scope.reloadData=1;
			/*
			 * When the selection is cleared, just truncate all the lists of selected 
			 * stuff to 0 and then reload the data for the grid (to unselect items.)
			 */
			$scope.clearSelection=function() {
				_.each($scope.selected_features, function (v, index) {
					$scope.gridOptions2.selectItem(index, false);
				});
				_.each($scope.data, function (v, index) {
					$scope.gridOptions.selectItem(index, false);
				});
				$scope.selected_features=[];
			}
			
			
			$scope.$on('leafletDirectiveMap.click', function(ev, e) {
				var lat=e.leafletEvent.latlng.lat;
				var long=e.leafletEvent.latlng.lng;
				var zoom=e.leafletMap.getZoom();
		        $scope.clearSelection();
		        $scope.feature_query_results=true
				var config={params: {lat: e.leafletEvent.latlng.lat,
									 lon: e.leafletEvent.latlng.lng,
									 zoom: e.leafletMap.getZoom(),
									 format: 'query'}};
				$http.get($scope.job_data.results, config).success(function (data) {
					//$log.info('Result from query was %s', data);
					$scope.selected_features=data.data;
				})
		    });
			function ngGridLayoutPlugin () {
			    var self = this;
			    this.grid = null;
			    this.scope = null;
			    this.init = function(scope, grid, services) {
			        self.domUtilityService = services.DomUtilityService;
			        self.grid = grid;
			        self.scope = scope;
			    };
			
			    this.updateGridLayout = function () {
			        if (!self.scope.$$phase) {
			            self.scope.$apply(function(){
			                self.domUtilityService.RebuildGrid(self.scope, self.grid);
			            });
			        }
			        else {
			            // $digest or $apply already in progress
			            self.domUtilityService.RebuildGrid(self.scope, self.grid);
			        }
			    };
			}
			
			$scope.selected_selected=[];
			var layoutPlugin = new ngGridLayoutPlugin();
			$scope.updateLayout = function(){
			      layoutPlugin.updateGridLayout();
			};
		
		    $scope.gridOptions2={data: 'selected_features',
		    		             showColumnMenu: false,
		    		             plugins: [layoutPlugin],
		    		             multiSelect: false,
		    		             columnDefs: 'columnOptions',
		    		             showFooter: false,
		    		             selectedItems: $scope.selected_selected}
		    
			$scope.gridOptions= {data: 'data',
								 columnDefs: 'columnOptions',
		//						 enablePaging: true,
								 showFooter: true,
								 multiSelect: true,
								 selectedItems: $scope.selections,
								 totalServerItems: 'totalServerItems',
								 sortInfo: $scope.sortInfo,
		//						 pagingOptions: $scope.pagingOptions,
								 filterOptions: $scope.filterOptions,
								 useExternalSorting: true,
			                     showColumnMenu: false };
			_.each(['filterOptions', 'sortInfo'], function (item) {
				$scope.$watch(item, function (newVal, oldVal) {
					$log.info('Got change to ', item, newVal, oldVal);
					if (newVal !== oldVal) {
						if ($scope.sortInfo.fields.length) {
						   $scope.sort_field=$scope.sortInfo.fields[0]
						   if ($scope.sortInfo.directions[0] == 'desc') {
							   $scope.sort_field='-'+$scope.sort_field;
						   }
						}
						$scope.getPagedDataAsync($scope.page_size, 
								                 0,
								                 $scope.filterOptions.filterText,
								                 $scope.sort_field);
					}
				}, true);
			});
			
			
			
			
			/* 
			 * The leaflet directive code is somewhat broke in that if 
			 * bounds is specified, but set to a variable set to null, it is then 
			 * totally ignored (the watch isn't setup.)  To mitigate this, set the
			 * bounds to some reasonable value to start with, then we can change it
			 * later since the $watch is there...
			 */
			$scope.bounds={southWest: { lat: 44.81773,
				                        lng: -93.499378},
				           northEast: { lat: 45.076137,
				                        lng: -93.16212 }
						  };
		
			
			var style=function (feature) {
				geojsonMarkerOptions = {
						    radius: 8,
						    fillColor: "#ff7800",
						    color: "#000",
						    weight: 1,
						    opacity: 1,
						    fillOpacity: 0.8
						};
				return geojsonMarkerOptions;
			}
			$scope.leaflet={'defaults': { tileLayer: 'http://{s}.tile.cloudmade.com/{key}/{styleId}/256/{z}/{x}/{y}.png',
										  tileLayerOptions: { key: '0c9dbe8158f6482d84e3543b1a790dbb', styleId: 997 },
										  maxZoom: 18
										},
					        'layers': {
					        		   'baselayers': {cloudmade: { top: true,
													               name: 'Cloudmade (OSM Data)',
													               type: 'xyz',
													               url: 'http://{s}.tile.cloudmade.com/{key}/{styleId}/256/{z}/{x}/{y}.png',
													               layerParams: {
													                   key: '0c9dbe8158f6482d84e3543b1a790dbb',
													                   styleId: 997
													               },
													               layerOptions: {
													                   subdomains: ['a', 'b', 'c'],
													                   continuousWorld: false,
														               opacity: .5,
													               }
													             }
										        	 },
									   'overlays': { }
					        }
					        
			}
			
			// Get the information about the input file - used to determine if this
			// job has a spatial component to it and get the various URLs for data
			// display.
			$scope.resources['job'].one($scope.jobid).get().then(function (job_data) {
				// Store the job data, then get the input file data as well, so we
				// can determine what the input file fields are, and also so we can
				// figure out if there is a spatial component to the results.
				$scope.job_data=job_data;
				var file_id=job_data.data_file.split('/').reverse()[1];
				$scope.input_data=$scope.resources['datafile'].one(file_id).get().then(function (input_data) {
					if (input_data.geom_type) {
						$scope.bounds=getBounds(input_data.bbox);
					}
					$scope.input_data=input_data;
					// Don't get the paged results until we load the datafile information,
					// otherwise we cannot figure out the columns to display.
					$scope.getPagedDataAsync($scope.page_size, 0, '', 'nmtk_id');
				});
				
				$scope.leaflet.layers.overlays['results']= {
		            name: 'Tool Results',
		            type: 'wms',
		            visible: true,
		            url: $scope.job_data.wms_url,
		            layerOptions: { layers: $scope.job_data.layer,
		                    		format: 'image/png',
		                    		transparent: true }
		    	};
				
				
				
			});
			
			
			// Handle the case when a user clicks on a spot on the map, we need to then
			// fire off a GetFeatureInfo requests against the WMS.
			
		     
			$scope.close=function () {
				$scope.$parent.results_job=undefined;
				$location.path('/job/');
			}
		}
	];
	return controller;
});

