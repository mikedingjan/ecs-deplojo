import os

from ecs_deplojo import task_definitions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_generate_task_definition(tmpdir):
    task_data = """
    {
      "family": "default",
      "volumes": [],
      "containerDefinitions": [
        {
          "name": "default",
          "image": "${image}",
          "essential": true,
          "command": ["hello", "world"],
          "memory": 256,
          "cpu": 0,
          "portMappings": [
            {
              "containerPort": 8080,
              "hostPort": 0
            }
          ]
        }
      ]
    }
    """.strip()

    filename = tmpdir.join('task_definition.json')
    filename.write(task_data)

    result = task_definitions.generate_task_definition(
        filename.strpath,
        environment={},
        template_vars={
            'image': 'my-docker-image:1.0',
        },
        overrides={},
        name='my-task-def',
    )
    expected = {
        'family': 'my-task-def',
        'volumes': [],
        'containerDefinitions': [
            {
                'name': 'default',
                'image': 'my-docker-image:1.0',
                'essential': True,
                'command': ['hello', 'world'],
                'memory': 256,
                'cpu': 0,
                'portMappings': [
                    {
                        'containerPort': 8080,
                        'hostPort': 0
                    }
                ],
                'environment': {}
            }
        ]
    }
    assert result == expected


def test_generate_task_definition_overrides(tmpdir):
    task_data = """
    {
      "family": "default",
      "volumes": [],
      "containerDefinitions": [
        {
          "name": "default",
          "image": "${image}",
          "essential": true,
          "command": ["hello", "world"],
          "memory": 256,
          "cpu": 0,
          "portMappings": [
            {
              "containerPort": 8080,
              "hostPort": 0
            }
          ]
        }
      ]
    }
    """.strip()

    filename = tmpdir.join('task_definition.json')
    filename.write(task_data)

    result = task_definitions.generate_task_definition(
        filename.strpath,
        environment={},
        template_vars={
            'image': 'my-docker-image:1.0',
        },
        overrides={
            'default': {
                'memory': 512,
                'memoryReservation': 128,
                'portMappings': [
                    {
                        'hostPort': 80,
                        'containerPort': 9000,
                    }
                ],
            }
        },
        name='my-task-def',
    )
    expected = {
        'family': 'my-task-def',
        'volumes': [],
        'containerDefinitions': [
            {
                'name': 'default',
                'image': 'my-docker-image:1.0',
                'essential': True,
                'command': ['hello', 'world'],
                'memory': 512,
                'memoryReservation': 128,
                'cpu': 0,
                'portMappings': [
                    {
                        'containerPort': 8080,
                        'hostPort': 0
                    },
                    {
                        'containerPort': 9000,
                        'hostPort': 80
                    }
                ],
                'environment': {}
            }
        ]
    }
    assert result == expected


def test_generate_task_definitions(tmpdir):
    task_data = """
    {
      "family": "default",
      "volumes": [],
      "containerDefinitions": [
        {
          "name": "web-1",
          "image": "${image}",
          "essential": true,
          "command": ["hello", "world"],
          "memory": 256,
          "cpu": 0,
          "portMappings": [
            {
              "containerPort": 8080,
              "hostPort": 0
            }
          ]
        },
        {
          "name": "web-2",
          "image": "${image}",
          "essential": true,
          "command": ["hello", "world"],
          "memory": 256,
          "cpu": 0,
          "portMappings": [
            {
              "containerPort": 8080,
              "hostPort": 0
            }
          ]
        }
      ]
    }
    """.strip()

    filename = tmpdir.join('task_definition.json')
    filename.write(task_data)

    config = {
        'environment': {
            'DATABASE_URL': 'postgresql://',
        },
        'environment_groups': {
            'group-1': {
                'ENV_CODE': 'group-1',
            },
            'group-2': {
                'ENV_CODE': 'group-2',
            },
        },
        'task_definitions': {
            'task-def-1': {
                'template': filename.strpath,
                'environment_group': 'group-1',
                'overrides': {
                    'web-1': {
                        'memory': 512,
                    }
                }
            },
            'task-def-2': {
                'template': filename.strpath,
                'environment_group': 'group-2',
                'overrides': {
                    'web-1': {
                        'memory': 512,
                    }
                }
            }
        }
    }

    result = task_definitions.generate_task_definitions(
        config,
        template_vars={
            'image': 'my-docker-image:1.0',
        },
        base_path=None)

    expected = {
        'task-def-1': {
            'definition': {
                'family': 'task-def-1',
                'volumes': [],
                'containerDefinitions': [
                    {
                        'name': 'web-1',
                        'image': 'my-docker-image:1.0',
                        'essential': True,
                        'command': ['hello', 'world'],
                        'memory': 512,
                        'cpu': 0,
                        'portMappings': [
                            {
                                'containerPort': 8080,
                                'hostPort': 0
                            }
                        ],
                        'environment': {
                            'DATABASE_URL': 'postgresql://',
                            'ENV_CODE': 'group-1',
                        }
                    },
                    {
                        'name': 'web-2',
                        'image': 'my-docker-image:1.0',
                        'essential': True,
                        'command': ['hello', 'world'],
                        'memory': 256,
                        'cpu': 0,
                        'portMappings': [
                            {
                                'containerPort': 8080,
                                'hostPort': 0
                            }
                        ],
                        'environment': {
                            'DATABASE_URL': 'postgresql://',
                            'ENV_CODE': 'group-1',
                        }
                    }
                ]
            },
        },
        'task-def-2': {
            'definition': {
                'family': 'task-def-2',
                'volumes': [],
                'containerDefinitions': [
                    {
                        'name': 'web-1',
                        'image': 'my-docker-image:1.0',
                        'essential': True,
                        'command': ['hello', 'world'],
                        'memory': 512,
                        'cpu': 0,
                        'portMappings': [
                            {
                                'containerPort': 8080,
                                'hostPort': 0
                            }
                        ],
                        'environment': {
                            'DATABASE_URL': 'postgresql://',
                            'ENV_CODE': 'group-2',
                        }
                    },
                    {
                        'name': 'web-2',
                        'image': 'my-docker-image:1.0',
                        'essential': True,
                        'command': ['hello', 'world'],
                        'memory': 256,
                        'cpu': 0,
                        'portMappings': [
                            {
                                'containerPort': 8080,
                                'hostPort': 0
                            }
                        ],
                        'environment': {
                            'DATABASE_URL': 'postgresql://',
                            'ENV_CODE': 'group-2',
                        }
                    }
                ]
            }
        }
    }
    assert result == expected
